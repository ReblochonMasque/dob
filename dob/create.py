# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

import json
import os
import random
import traceback

from gettext import gettext as _

import click
from inflector import English, Inflector

from nark.helpers.parsing import ParserException

from dob_viewer import interrogate
from dob_viewer.config.styling.classes_style import (
    load_classes_style,
    load_matches_style
)
from dob_viewer.config.styling.content_lexer import load_content_lexer
from dob_viewer.config.styling.no_completion import load_no_completion
from dob_viewer.crud.fact_dressed import FactDressed

from .clickux.echo_assist import click_echo, echo_block_header
from .config.app_dirs import AppDirs, get_appdirs_subdir_file_path
from .helpers import (
    dob_in_user_exit,
    dob_in_user_warning,
    echo_fact,
    highlight_value
)
from .helpers.crude_progress import CrudeProgress
from .helpers.emphasis import attr, fg
from .helpers.fix_times import (
    mend_fact_timey_wimey,
    reduce_time_hint
)

__all__ = (
    'add_fact',
    'cancel_fact',
    'mend_facts_confirm_and_save_maybe',
    'prompt_and_save',
    # Private:
    #   'echo_ongoing_completed',
    #   'must_confirm_fact_edits',
    #   'must_create_fact_from_factoid',
    #   'save_facts_maybe',
)


# ***

def add_fact(
    controller,
    factoid,
    time_hint,
    use_carousel=False,
    edit_text=False,
    edit_meta=False,
    yes=False,
    dry=False,
):
    """
    Start or add a fact.

    Args:
        factoid (str): ``factoid`` detailing Fact to be added.
            See elsewhere for the factoid format.

        time_hint (str, optional): One of:
            | 'verify_none': Do not expect to find any time encoded in factoid.
            | 'verify_both': Expect to find both start and end times.
            | 'verify_start': Expect to find just one time, which is the start.
            | 'verify_end': Expect to find just one time, which is the end.
            | 'verify_then': Optional time is new start; and either extend
            ongoing fact to new start, or back-fill interval gap.
            | 'verify_still': Optional time is new start; copy prev meta to new Fact;
            either extend ongoing fact, or back-fill interval gap.
            | 'verify_after': No time spec. Start new Fact at time of previous end.

        yes (bool, optional): If True, update other Facts changed by the new
            fact being added (affects other Facts' start/end/deleted attrs).
            If False, prompt user (i.e., using fancy interface built with
            python-prompt-toolkit) for each conflict.

        edit_meta (bool, optional): If True, prompt user for activity and/or
            category, if not indicated; and prompt user for tags. Shows
            MRU lists to try to make it easy for user to specify commonly
            used items.

    Returns:
        Nothing: If everything went alright. (Otherwise, will have exited.)
    """

    def _add_fact():
        new_fact = _create_fact()
        new_fact_or_two, conflicts = _mend_times(new_fact)
        edit_facts, orig_facts = _prepare_facts(new_fact_or_two)
        edit_fact = _add_conflicts(conflicts, edit_facts, orig_facts)
        _maybe_prompt_description(edit_fact)
        _maybe_prompt_actegory(edit_fact)
        saved_facts = _prompt_and_save(edit_facts, orig_facts)
        return saved_facts

    def _create_fact():
        # NOTE: factoid is an ordered tuple of args; e.g., sys.argv[2:], if
        #       sys.argv[0] is the executable name, and sys.argv[1] is command.
        #       Because dob is totes legit, it does not insist that the user
        #       necessary quote anything on the command line, but it does not
        #       insist not, either, so factoid might have just one element (a
        #       string) containing all the information; or factoid might be a
        #       list of strings that need to be parsed and reassembled (though
        #       not necessarily in that order).
        #
        #         tl;dr: factoid is a tuple of 1+ strings that together specify the Fact.

        # Make a new Fact from the command line input.
        new_fact = must_create_fact_from_factoid(
            controller, factoid, time_hint,
        )
        return new_fact

    def _mend_times(new_fact):
        # If there's an ongoing Fact, we might extend or squash it.
        # Also, if the new Fact overlaps existing Facts, those Facts'
        # times might be changed, and/or existing Facts might be deleted.
        try:
            new_fact_or_two, conflicts = mend_fact_timey_wimey(
                controller, new_fact, time_hint,
            )
        except ValueError as err:
            # (lb): I'm very indecisive.
            choices = [
                _("Not so fast!"),
                _("Cannawt!"),
                _("Unpossible!"),
                _("Insidious!"),
                _("Think again!"),
            ]
            msg = _('{} {}').format(random.choice(choices), err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        return new_fact_or_two, conflicts

    def _prepare_facts(new_fact_or_two):
        edit_facts = []
        orig_facts = []
        new_fact_pk = -1
        for new_fact in new_fact_or_two:
            # If ongoing was squashed, edited_fact.pk > 0, else < 0.
            # There might also be an extended filler gap Fact added.
            if new_fact.pk is None:
                new_fact.pk = new_fact_pk
                new_fact_pk -= 1
                edit_facts.append(new_fact)
            else:
                # The edited fact is in conflicts, and carousel will start on it.
                assert new_fact.pk > 0
        return edit_facts, orig_facts

    def _add_conflicts(conflicts, edit_facts, orig_facts):
        for edited, original in conflicts:
            edit_facts.append(edited)
            # (lb): This is the only place orig_facts is not [edit_fact.copy(), ...].
            orig_facts.append(original)
        edit_fact = edit_facts[0]
        return edit_fact

    def _maybe_prompt_description(edit_fact):
        if not edit_text:
            return

        # User wants to edit description first.
        interrogate.ask_user_for_edits(
            controller,
            fact=edit_fact,
            always_ask=False,
            restrict_edit='description',
        )

    def _maybe_prompt_actegory(edit_fact):
        if not edit_meta:
            return

        interrogate.ask_user_for_edits(
            controller,
            fact=edit_fact,
        )

    def _prompt_and_save(edit_facts, orig_facts):
        saved_facts = prompt_and_save(
            controller,
            edit_facts,
            orig_facts,
            use_carousel=use_carousel,
            yes=yes,
            dry=dry,
            progress=None,
        )
        return saved_facts

    return _add_fact()


# ***

def mend_facts_confirm_and_save_maybe(
    controller, fact, time_hint, other_edits, yes, dry,
):
    """"""
    def _mend_facts_confirm_and_save_maybe():
        new_fact_or_two, conflicts = mend_fact_timey_wimey(
            controller, fact, time_hint, other_edits,
        )
        saved_facts = confirm_conflicts_and_save_all(new_fact_or_two, conflicts)
        return saved_facts

    def confirm_conflicts_and_save_all(new_fact_or_two, conflicts):
        """"""
        # Ask user what to do about conflicts/edits.
        ignore_pks = other_edits.keys()
        must_confirm_fact_edits(controller, conflicts, yes, dry)
        saved_facts = save_facts_maybe(
            controller, new_fact_or_two, conflicts, ignore_pks, dry,
        )
        return saved_facts

    return _mend_facts_confirm_and_save_maybe()


# ***

def must_create_fact_from_factoid(
    controller, factoid, time_hint,
):

    def _must_create_fact_from_factoid(
        controller, factoid, time_hint,
    ):
        separators = must_prepare_factoid_item_separators(controller)
        use_hint = reduce_time_hint(time_hint)
        try:
            fact, err = FactDressed.create_from_factoid(
                factoid=factoid,
                time_hint=use_hint,
                separators=separators,
                lenient=True,
            )
            controller.client_logger.info(str(err)) if err else None
        except ParserException as err:
            msg = _('Oops! {}').format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        # This runs for verify_after, not verify_none/"blank time".
        fact_set_start_time_after_hack(fact, time_hint=use_hint)
        return fact

    def must_prepare_factoid_item_separators(controller):
        sep_string = controller.config['fact.separators']
        if not sep_string:
            return None
        try:
            separators = json.loads(sep_string)
        except json.decoder.JSONDecodeError as err:
            msg = _(
                "The 'separators' config value is not valid JSON: {}"
            ).format(err)
            controller.client_logger.error(msg)
            dob_in_user_exit(msg)
        return separators

    # FIXME/DRY: See create.py/transcode.py (other places that use "+0").
    #   (lb): 2019-01-22: Or maybe I don't care (not special enough to DRY?).
    #   (lb): 2019-12-06: My knowledge of this code is now so crusty that
    #                     it's too dangerous to consider DRYing anything!
    #                     Especially not without good test coverage first.
    def fact_set_start_time_after_hack(fact, time_hint):
        # FIXME/2019-01-19 13:00: What about verify_next: and verify_then: ???
        #   TESTME: Write more tests first to see if there's really an issue.
        if time_hint != "verify_after":
            return
        assert fact.start is None and fact.end is None
        # (lb): How's this for a hack!?
        fact.start = "+0"

    # ***

    return _must_create_fact_from_factoid(controller, factoid, time_hint)


# ***

def must_confirm_fact_edits(controller, conflicts, yes, dry):
    """"""

    def _must_confirm_fact_edits(conflicts, yes, dry):
        conflicts = cull_stopped_ongoing(conflicts)
        if not conflicts:
            return

        yes = yes or dry
        if not yes:
            echo_confirmation_banner(conflicts)

        n_conflict = 0
        n_confirms = 0
        for edited_fact, original in conflicts:
            n_conflict += 1
            if not yes:
                confirmed = echo_confirmation_edited(
                    n_conflict, edited_fact, original,
                )
                n_confirms += 1 if confirmed else 0
            else:
                controller.client_logger.debug(
                    _('Editing fact: {}').format(edited_fact)
                )

        if n_conflict != n_confirms:
            # (lb): This function is not used by the carousel -- only by
            # one-off CLI commands -- so blowing up here is perfectly fine.
            # (The carousel has its own error message display mechanism;
            #  and more importantly the carousel should never die,
            #  but should only ever be asked to die by the user.)
            dob_in_user_exit(_("Please try again."))

    def cull_stopped_ongoing(conflicts):
        return [con for con in conflicts if 'stopped' not in con[0].dirty_reasons]

    def echo_confirmation_banner(conflicts):
        click.echo()
        click.echo(_(
            'Found {}{}{} {}. '
            '{}Please confirm the following changes:{}'
            .format(
                fg('magenta'), len(conflicts), attr('reset'),
                Inflector(English).conditional_plural(len(conflicts), 'conflict'),
                attr('underlined'), attr('reset'),
            )
        ))

    def echo_confirmation_edited(n_conflict, edited_fact, original):
        click.echo()
        # MAYBE:
        #   from dob_viewer.helpers.re_confirm import confirm
        #   confirmed = confirm()
        confirmed = click.confirm(
            text=_('Conflict #{}\n-----------\n{}\nReally edit fact?').format(
                n_conflict,
                original.friendly_diff(edited_fact),
            ),
            default=False,
            abort=False,
            # prompt_suffix=': ',
            # show_default=True,
            # err=False,
        )
        return confirmed

    # ***

    _must_confirm_fact_edits(conflicts, yes, dry)


# ***

def save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry):
    """"""

    def _save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry):
        new_and_edited = []
        if conflicts and dry:
            echo_dry_run()
        for edited_fact, original in conflicts:
            if not dry:
                new_and_edited += save_fact(controller, edited_fact, dry)
                if 'stopped' in edited_fact.dirty_reasons:
                    # This'll happen on one-off dob-to/dob-at/etc., but it
                    # will not happen on dob-import, e.g., if dob-import
                    # closes ongoing fact, it'll be saved normally, and it
                    # will not be passed herein as part of conflicts.
                    echo_ongoing_completed(controller, edited_fact)
            else:
                click.echo(original.friendly_diff(edited_fact))

        for fact in new_facts:
            new_and_edited += save_fact(controller, fact, dry, ignore_pks=ignore_pks)
        return new_and_edited

    def echo_dry_run():
        click.echo()
        click.echo('{}Dry run! These facts will be edited{}:\n '.format(
            attr('underlined'),
            attr('reset'),
        ))

    def save_fact(controller, fact, dry, ignore_pks=[]):
        # (lb): SIMILAR: edits_manager.save_edited_fact, create.save_fact.
        if fact.pk and fact.pk < 0:
            fact.pk = None
        if fact.pk is None and fact.deleted:
            controller.client_logger.debug('{}: {}'.format(_('Dead fact'), fact.short))
            return []
        if not dry:
            controller.client_logger.debug('{}: {}'.format(_('Save fact'), fact.short))
            try:
                new_fact = controller.facts.save(fact, ignore_pks=ignore_pks)
            except Exception as err:
                traceback.print_exc()
                dob_in_user_exit(str(err))
        else:
            new_fact = fact
            echo_fact(fact)
        return [new_fact, ]

    # ***

    return _save_facts_maybe(controller, new_facts, conflicts, ignore_pks, dry)


# ***

def cancel_fact(controller, purge=False):
    """
    Cancel current fact, either marking it deleted, or really removing it.

    Returns:
        None: If success.

    Raises:
        KeyErŕor: No *ongoing fact* can be found.
    """
    try:
        fact = controller.facts.cancel_current_fact(purge=purge)
    except KeyError:
        message = _("Nothing tracked right now. Not doing anything.")
        controller.client_logger.info(message)
        raise click.ClickException(message)
    else:
        echo_ongoing_completed(controller, fact, cancelled=True)
        return fact


# ***

def echo_ongoing_completed(controller, fact, cancelled=False):
    """"""
    def _echo_ongoing_completed():
        colorful = controller.config['term.use_color']
        leader = _('Completed: ') if not cancelled else _('Cancelled: ')
        cut_width = width_avail(len(leader))
        completed_msg = echo_fact(leader, colorful, cut_width)
        controller.client_logger.debug(completed_msg)

    def width_avail(leader_len):
        term_width = click.get_terminal_size()[0]
        width_avail = term_width - leader_len
        return width_avail

    def echo_fact(leader, colorful, cut_width):
        completed_msg = (
            leader
            + fact.friendly_str(
                shellify=False,
                description_sep=': ',

                # FIXME: (lb): Implement localize.
                # FIXME/2018-06-10: (lb): fact being saved as UTC
                localize=True,

                colorful=colorful,

                # FIXME/2018-06-12: (lb): Too wide (wraps to next line);
                # doesn't account for leading fact parts (times, act@gory, tags).
                cut_width=cut_width,

                show_elapsed=True,
            )
        )
        click_echo(completed_msg)
        return completed_msg

    _echo_ongoing_completed()


# ***

def prompt_and_save(
    controller,
    edit_facts=None,
    orig_facts=None,
    file_in=None,
    file_out=None,
    rule='',
    backup=True,
    leave_backup=False,
    use_carousel=False,
    yes=False,
    dry=False,
    progress=None,
    **kwargs,
):
    """"""
    progress = CrudeProgress(enabled=True) if progress is None else progress

    def _prompt_and_save():
        backup_f = prepare_backup_file(backup)
        delete_backup = False
        inner_error = None
        saved_facts = []
        try:
            saved_facts = prompt_persist(backup_f)
            delete_backup = True
        except SystemExit:
            # Explicit sys.exit() from our code.
            # The str(err) is just the exit code #.
            raise
        except BaseException as err:
            # NOTE: Using BaseException, not just Exception, so that we
            #       always catch (KeyboardInterrupt, SystemExit), etc.
            # Don't cleanup backup file.
            traceback.print_exc()
            inner_error = str(err)
        finally:
            if not delete_backup:
                traceback.print_exc()
                msg = 'Something horrible happened!'
                if inner_error is not None:
                    msg += _(' err: "{}"').format(inner_error)
                if backup_f:
                    msg += (
                        _("\nBut don't worry. A backup of edits was saved at: {}")
                        .format(backup_f.name)
                    )
                dob_in_user_exit(msg)
            cleanup_files(backup_f, file_out, delete_backup)
        return saved_facts

    # ***

    def prepare_backup_file(backup):
        if not backup:
            return None
        backup_path, backup_link = get_import_ephemeral_backup_path()
        backup_f = None
        log_msg = _("Creating backup at {0}").format(backup_path)
        controller.client_logger.info(log_msg)
        try:
            backup_f = open(backup_path, 'w')
        except Exception as err:
            msg = (
                'Failed to create temporary backup file at "{}": {}'
                .format(backup_path, str(err))
            )
            dob_in_user_exit(msg)
        try:
            # NOTE: os.remove removes the file being linked; we want unlink.
            #   We also want lexists, not exists, to get True for broken links.
            os.unlink(backup_link) if os.path.lexists(backup_link) else None
            os.symlink(backup_path, backup_link)
        except Exception as err:
            msg = (
                'Failed to remove temporary backup file link at "{}": {}'
                .format(backup_link, str(err))
            )
            dob_in_user_warning(msg)
        return backup_f

    IMPORT_BACKUP_DIR = 'carousel'

    def get_import_ephemeral_backup_path():
        backup_prefix = 'dob.import'
        backup_tstamp = controller.now.strftime('%Y%m%d%H%M%S')
        backup_basename = backup_prefix + '-' + backup_tstamp
        backup_fullpath = get_appdirs_subdir_file_path(
            file_basename=backup_basename,
            dir_dirname=IMPORT_BACKUP_DIR,
            appdirs_dir=AppDirs.user_cache_dir,
        )
        # 2018-06-29 18:56: This symlink really isn't that helpful...
        #   but we'll see if I start using it. At least for DEVing.
        backup_linkpath = get_appdirs_subdir_file_path(
            file_basename=backup_prefix,
            dir_dirname=IMPORT_BACKUP_DIR,
            appdirs_dir=AppDirs.user_cache_dir,
        )
        return backup_fullpath, backup_linkpath

    def cleanup_files(backup_f, file_out, delete_backup):
        if backup_f:
            backup_f.close()
            if delete_backup:
                if not leave_backup:
                    try:
                        os.unlink(backup_f.name)
                    except FileNotFoundError:
                        # [lb]: 2019-01-17: Happening occasionally on dob-import
                        # testing, not sure if related dev_breakpoint usage, or
                        # not editing any Facts, or what, but not predictably
                        # recreating. Not a problem if it fails, but why would it
                        # fail, especially given that the code just called close().
                        controller.client_logger.warning(
                            'nothing to cleanup?: backup file missing: {}'
                            .format(backup_f.name)
                        )
                else:
                    click_echo(
                        _('Abandoned working backup at: {}')
                        .format(highlight_value(backup_f.name))
                    )
        # (lb): Click will close the file, but we can also cleanup first.
        if file_out and not dry:
            file_out.close()

    # ***

    def prompt_persist(backup_f):
        ready_facts, carousel = prompt_all(backup_f)
        persist_facts(ready_facts)
        # CLOSED_LOOP: (lb): whoa_nellie is (disabled) kludge to avoid abandoned
        # event loop RuntimeError (better solution is needed; but sleeping here
        # before app exit can anecdotally avoid issue. And by "anecdotal" I mean
        # not necessarily guaranteed, so not a proper solution (and not even a
        # proper "kludge" by more stringent standards)).
        carousel and carousel.whoa_nellie()
        return ready_facts

    # ***

    def prompt_all(backup_f):
        if not use_carousel:
            return ((edit_facts or []), None)

        backup_callback = write_facts_file(backup_f, rule, dry)
        classes_style = load_classes_style(controller)
        matches_style = load_matches_style(controller)
        content_lexer = load_content_lexer(controller)
        no_completion = load_no_completion(controller)

        # Lazy-load the carousel and save ~0.065s.
        from dob_viewer.traverser.carousel import Carousel

        carousel = Carousel(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            dirty_callback=backup_callback,
            dry=dry,
            classes_style=classes_style,
            matches_style=matches_style,
            content_lexer=content_lexer,
            no_completion=no_completion,
        )
        ready_facts = carousel.gallop(**kwargs)
        # The Carousel forces the user to save to exit! So ready_facts is empty!!
        # Or the user quit without saving, which would also mean no ready facts.
        # - 2020-01-28: (lb): If I recall correctly, I had originally
        #   plumbed Carousel to have you *review* Facts being imported
        #   (and only those Facts; user did not see other Facts); but now
        #   user sees Carousel of all Facts, with imported Facts inserted,
        #   but not saved, and user saves through Carousel.
        #   - Which is fine, probably desirable. But because user might
        #     have insisted `not use_carousel`, this module still has
        #     code to save Facts independent of the Carousel.
        #     Nonetheless, the Carousel is still coded to return a Facts
        #     array...
        #     MAYBE/2020-01-28: Could probably remove gallop() return list,
        #                  I think nowadays it'll always be the empty list??
        controller.affirm(not ready_facts)

        return ready_facts, carousel

    # ***

    def persist_facts(ready_facts):
        if not ready_facts:
            return
        record_ready_facts(ready_facts, file_out, dry)
        celebrate(ready_facts)

    def record_ready_facts(ready_facts, file_out, dry):
        task_descrip = _('Saving facts')
        term_width, dot_count, fact_sep = progress.start_crude_progressor(task_descrip)

        new_and_edited = []

        other_edits = {fact.pk: fact for fact in ready_facts}

        for idx, fact in enumerate(ready_facts):
            term_width, dot_count, fact_sep = progress.step_crude_progressor(
                task_descrip, term_width, dot_count, fact_sep,
            )

            is_first_fact = idx == 0
            is_final_fact = idx == (len(ready_facts) - 1)
            fact_pk = fact.pk
            new_and_edited += persist_fact(
                fact, other_edits, is_first_fact, is_final_fact, file_out, dry,
            )
            # If an existing Fact:
            #   - the pk is the same; and
            #   - the saved Fact is marked deleted, and a new one is created,
            #      or saved Fact is not marked deleted if it was ongoing Fact.
            # But if a new Fact, pk was < 0, now it's None, and new fact pk > 0.
            # Once saved, rely on Fact in store for checking conflicts.

            # If fact existed, fact.pk; else, fact_pk < 0 is in-app temp. ID.
            del other_edits[fact.pk is not None and fact.pk or fact_pk]

        assert len(other_edits) == 0

        # NOTE: It's up to the caller to ensure controller.post_process called,
        #       either via @post_processor, or by calling it directly.

        progress.click_echo_current_task('')

    def persist_fact(fact, other_edits, is_first_fact, is_final_fact, file_out, dry):
        new_and_edited = [fact, ]
        if not dry:
            # If user did not specify an output file, save to database
            # (otherwise, we may have been maintaining a temporary file).
            if not file_out:
                new_and_edited = persist_fact_save(
                    fact, is_final_fact, other_edits, dry,
                )
            else:
                write_fact_block_format(file_out, fact, rule, is_first_fact)
        else:
            echo_block_header(_('Fresh Fact!'))
            click_echo()
            echo_fact(fact)
            click_echo()
        return new_and_edited

    # ***

    def write_facts_file(fact_f, rule, dry):
        def wrapper(carousel):
            if dry or not fact_f:
                return
            fact_f.truncate(0)
            # (lb): truncate doesn't move the pointer (you can peek()), and while
            # write seems to still work, it feels best to reset the pointer.
            fact_f.seek(0)
            for idx, fact in enumerate(carousel.prepared_facts):
                # The Carousel should only send us facts that need to be
                # stored, which excludes deleted Facts that were never stored.
                controller.affirm((not fact.deleted) or (fact.pk > 0))
                write_fact_block_format(fact_f, fact, rule, is_first_fact=(idx == 0))
            fact_f.flush()

        return wrapper

    def write_fact_block_format(fact_f, fact, rule, is_first_fact):
        write_fact_separator(fact_f, rule, is_first_fact)
        friendly_str = fact.friendly_str(
            # description_sep='\n\n',
            description_sep=': ',
            shellify=False,
            colorful=False,
            omit_empty_actegory=True,
        )
        fact_f.write(friendly_str)

    RULE_WIDTH = 76  # How wide to print the between-facts separator.

    def write_fact_separator(fact_f, rule, is_first_fact):
        if is_first_fact:
            return
        fact_f.write('\n\n')
        if rule:
            fact_f.write('{}\n\n'.format(rule * RULE_WIDTH))

    def persist_fact_save(fact, is_final_fact, other_edits, dry):
        # (lb): This is a rudimentary check. I'm guessing other code
        # will prevent user from editing old Fact and deleting its
        # end, either creating a second ongoing Fact, OR, more weirdly,
        # creating an ongoing Fact that has closed Facts after it!
        # 2018-07-05/TEST_ME: Test previous comment: try deleting end of old Fact.
        # FIXME: Do we care to confirm if is_final_fact is indeed latest ever? Meh?
        time_hint = 'verify_both' if not is_final_fact else 'verify_last'
        new_and_edited = mend_facts_confirm_and_save_maybe(
            controller, fact, time_hint, other_edits, yes=yes, dry=dry,
        )
        return new_and_edited

    # ***

    def celebrate(ready_facts):
        if not ready_facts:
            return
        click_echo('{}{}{}! {}'.format(
            attr('underlined'),
            _('Voilà'),
            attr('reset'),
            _('Saved {} facts.').format(highlight_value(len(ready_facts))),
        ))

    return _prompt_and_save()

