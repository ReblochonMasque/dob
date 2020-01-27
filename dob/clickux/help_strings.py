# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

"""Module to provide u18n friendly help text strings for our CLI commands."""

from gettext import gettext as _

from nark.helpers.emphasis import attr, bg, coloring, fg

from .. import __arg0name__, __package_name__
from ..config.fileboss import default_config_path
from ..config.urable import ConfigUrable
from ..copyright import assemble_copyright
from ..helpers import highlight_value

# Note that the help formatter reformats paragraphs when the help is
# displayed, to a width determined by the terminal and max_content_width.
# So the newlines you see in the text below will be removed and each
# paragraph will be reformatted with indents and new newlines inserted.
# - Your best bet to see how the text is formatted is to run the help.

# Note also that a lot of the help text is assembled at runtime, after
# dob has started and parsed command line arguments and configuration
# settings. This is because the global coloring() switch is off until
# after arguments are parsed and the config is read, and then it might
# be turned. But the way coloring works, ANSI is stripped when strings
# are assembled, as opposed to ANSI being stripped on output (the latter
# would make it easier to turn color on or off without having to rebuild
# strings, or to worry about when strings are generated; but our code is
# built the other way, so we have to wait for the coloring() question to
# be settled before building help text. Hence all the callbacks below.
#
# E.g., instead of seeing help text built like this:
#
#           SOME_HELP_TEXT = _("""Helps you.""")
#
#       you'll often see a builder method used instead, such as:
#
#           def SOME_HELP_TEXT(ctx):
#               return _("""Helps {color}you{reset}.""").format(...)

# ***
# *** [COMMON] Oft-used format() args.
# ***


def common_format():
    # (lb): Eh: This is a method because ENABLE_COLORS is False on startup,
    # and fg and attr will return empty strings if called when module is
    # sourced. So wait until help strings are built and it's known if color
    # or not.
    common_format = {
        'appname': highlight_value(__package_name__),
        'rawname': __package_name__,
        'codehi': fg('turquoise_2'),
        'reset': attr('reset'),
        'bold': attr('bold'),
        'italic': attr('italic'),
        'underlined': attr('underlined'),
        'wordhi': fg('chartreuse_3a'),
    }
    return common_format


# ***
# *** [BARE] Command help.
# ***

def RUN_HELP_WHATIS():
    _help = _(
        """
        {appname} is a time tracker for the command line.
        """.strip().format(**common_format())
    )
    return _help


def RUN_HELP_TRYME():
    _help = _(
        """
        - Try the demo to get acquainted with dob quickly,

          {codehi}{rawname} demo{reset}
        """.strip().format(**common_format())
    )
    return _help


def RUN_HELP_HEADER():
    _help = _(
        """
        {what_is}

        {try_me}
        """.strip().format(
            what_is=RUN_HELP_WHATIS(),
            try_me=RUN_HELP_TRYME(),
            **common_format()
        )
    )
    return _help


def RUN_HELP_TLDR():
    _help = _(
        """
        {what_is}

        - To read lots more help, run the help command,

         \b
         {codehi}{rawname} help{reset}

        - To learn to dob quick and easy, try the demo,

         \b
         {codehi}{rawname} demo{reset}

        \b
        {copyright}
        """.strip().format(
            what_is=RUN_HELP_WHATIS(),
            try_me=RUN_HELP_TRYME(),
            copyright='\b\n        '.join(assemble_copyright()),
            **common_format()
        )
    )
    return _help


def RUN_HELP_COMPLETE():
    _help = _(
        """
        {run_help_header}

        - Use {italic}help{reset} with any command to learn more, e.g.,

          {codehi}{rawname} init --help{reset}

          {codehi}{rawname} help init{reset}

          {codehi}{rawname} edit -h{reset}

        - Put global options {italic}before{reset} the command name, e.g.,

          {codehi}{rawname} --no-color details{reset}

        - See how {rawname} can {italic}hack your life{reset} using plugins,

          {codehi}{rawname} plugins avail{reset} [FIXME: No such cmd!]

        - Some commands have aliases, shown in (parentheses) below, e.g.,

          {codehi}{rawname} details{reset} {equalityop} {codehi}{rawname} info{reset}

        - For code rights and legal info, review the {copyrt_sym} and {scroll_sym},

          {codehi}{rawname} copyright{reset}

          {codehi}{rawname} license{reset}
        """.strip().format(
            run_help_header=RUN_HELP_HEADER(),
            equalityop=coloring() and '≡' or '==',
            copyrt_sym=coloring() and '©' or 'copyright',
            scroll_sym=coloring() and '📜' or 'license',
            **common_format()
        )
    )
    return _help


def RUN_HELP_OVERVIEW(ctx):
    if (
        (ctx.command.name == 'run')
        and (
            ctx.invoked_subcommand
            or ctx.help_option_spotted
        )
    ):
        return RUN_HELP_COMPLETE()
    return RUN_HELP_TLDR()


# ***
# *** [HELP] Command help.
# ***

HELP_HELP = _(
    """
    Prints help for the application or for the specified command.
    """
)


# ***
# *** [VERSION] Command help.
# ***

VERSION_HELP = _(
    """
    Prints the interface and library versions.
    """
)


# ***
# *** [LICENSE] Command help.
# ***

LICENSE_HELP = _(
    """
    Prints the software license.
    """
)


# ***
# *** [LICENSE] Command help.
# ***

COPYRIGHT_HELP = _(
    """
    Prints the software copyright.
    """
)


ABOUT_COMMAND_HELP = _(
    """
    Alias of 'copyright' command.
    """
)


# ***
# *** [DETAILS] Command help.
# ***

DETAILS_HELP = _(
    """
    Prints details about the runtime environment.
    """
)


DETAILS_TMI_HELP = _(
    """
    Show AppDirs paths, too.
    """
)

# ***
# *** [ENVIRONS] Command help.
# ***

ENVIRONS_HELP = _(
    """
    Prints shell-sourceable details about the runtime environment.

    Useful for setting up shell scripting, e.g.,

       \b
       eval "$({} environs)"
       echo $DOB_CONF
    """.format(__arg0name__)
)


# ***
# *** [DEBUG] Command help.
# ***

DEBUG_HELP = _(
    """
    Hidden command to break into a REPL prompt and poke around dob internals.

    This command is mostly an example to show developers how to easily debug.

    You'll probably want to just sprinkle your own breakpoints where you
    need them, e.g.,

      import sys, pdb; pdb.set_trace()

    or, if you're breaking into code after something stole the input,
    fix it first,

      import os, pdb; os.system("stty sane"); pdb.set_trace()
    """
)


# ***
# *** [DEMO] Command help.
# ***

def DEMO_HELP(ctx):
    _help = _(
        """
        Teaches you how to {rawname} -- {italic}Run this first!{reset}
        """
    ).strip().format(**common_format())
    return _help


# ***
# *** [INDUCTEE] help.
# ***

def NEWBIE_HELP_WELCOME(ctx):
    _help = _(
        """
        {color}┏━━━━━━━━━━━━━━━━━┓{reset}
        {color}┃ Welcome to dob! ┃{reset}
        {color}┗━━━━━━━━━━━━━━━━━┛{reset}
        """
    ).strip().format(
        color=(fg('spring_green_2a') + attr('bold')),
        # color=(fg('turquoise_4') + attr('bold')),
        # color=(fg('magenta_2a') + attr('bold')),
        # color=(fg('dark_orange_3b') + attr('bold')),
        **common_format(),
    )
    return _help


def section_heading(title):
    return _(
        """
        {color}{title}{reset}
        {line_color}{sep:{sep}<{len_title}}{reset}
        """
    ).strip().format(
        title=title,
        # sep='-',
        sep='─',
        len_title=len(title),
        # color=fg('spring_green_2a'),
        # color=fg('dark_orange'),
        # color=fg('turquoise_4'),
        # line_color=fg('grey_78'),
        # line_color=fg('light_blue'),
        line_color='',
        color='',
        **common_format()
    )


def NEWBIE_HELP_ONBOARDING(ctx):
    # NOTE: This help is not automatically formatted like other text.
    _help = _(
        """
        {banner}

        Let’s get you setup!

        {init_title}
        To create a fresh, empty database, run:

          {cmd_color}{appname} init{reset}

        {upgrade_title}
        To learn how to import data from a previous version
        of dob, or to import from the old hamster app, run:

          {cmd_color}{appname} migrate -h{reset}

        {demo_title}
        If you’d like to get your hands dirty, you can demo
        the application with some example data that you can
        follow as a walk-through. Run:

          {cmd_color}{appname} demo{reset}
        \b
        """
    ).format(
        appname=__arg0name__,
        banner=NEWBIE_HELP_WELCOME(ctx),
        upgrade_title=section_heading(_('Import existing facts')),
        init_title=section_heading(_('Start from scratch')),
        demo_title=section_heading(_('Demo Dob')),
        help_title=section_heading(_('Such Help')),
        cmd_color=fg('spring_green_2a'),
        **common_format(),
    )
    return _help


def NEWBIE_HELP_CREATE_CONFIG(ctx, cfg_path):
    _help = _(
        """
        {errcol}ERROR: No config file found at: “{cfg_path}”{reset}

        Where's your config file??

        Verify and correct the configuration file path.

        The configuration file defaults to:

            {default_config_path}

        but you can override it using an environ:

            {envkey}=PATH

        or by specifying a global option:

            -C/--configfile PATH

        If you are certain the path is correct and you want to create
        a new configuration file at the path specified, run init, e.g.,:

            {rawname} -C "{cfg_path}" init
        """
    ).strip().format(
        # FIXME/2019-11-19 14:42: Make wrapper for format() with common colors defined.
        # - Maybe change errors to white on red, like here,
        #   but only for white on black terms (based on some setting?).
        errcol=(bg('red_1') + attr('bold')),
        cfg_path=cfg_path,
        default_config_path=default_config_path(),
        envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
        **common_format()
    )
    return _help


def NEWBIE_HELP_REPAIR_CONFIG(ctx, cfg_path):
    _help = _(
        """
        {errcol}ERROR: Please fix the config file found at: “{cfg_path}”{reset}

        The configuration file is at least missing the db.orm setting, if not others.

        Either edit and repair the confirguration file manually, or blow it away:

            {rawname} config create --force
        """
    ).strip().format(
        # FIXME/2019-11-19 14:42: Make wrapper for format() with common colors defined.
        # - Maybe change errors to white on red, like here,
        #   but only for white on black terms (based on some setting?).
        errcol=(bg('red_1') + attr('bold')),
        cfg_path=cfg_path,
        default_config_path=default_config_path(),
        envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
        **common_format()
    )
    return _help


def NEWBIE_HELP_CREATE_STORE(ctx):
    _help = _(
        """
        {banner}

        Where's you database??

        FIXME: Provide example commands.

        """
    ).strip().format(
        # appname=__arg0name__,
        banner=NEWBIE_HELP_WELCOME(ctx),
        # mintgreen=(fg('spring_green_2a') + attr('bold')),
        # reset=attr('reset'),
        # **common_format()
    )
    return _help


# ***
# *** [INIT] Command help.
# ***

def INIT_HELP_OVERVIEW(ctx):
    controller = ctx.obj

    _hint_sqlite = ''
    if controller.config['db.engine'] == 'sqlite':
        _hint_sqlite = _(
            """
        And if you know SQL, you can poke around the database file easily:

         \b
         {codehi}# Assuming sqlite3 is installed:{reset}
         {codehi}sqlite3 {cfg_db_path}{reset}

        But you'll probably just want to make sure you backup that file!
            """.strip().format(
                default_config_path=highlight_value(default_config_path()),
                cfg_db_path=controller.config['db.path'],
                **common_format()
            )
        )

    _help = _(
        """
        Creates a default configuration file, and an empty database.

        - Unless it exists, init will create a default configuration at:

         \b
         {default_config_path}

        - Unless it exists, init will create an empty database file at:

         \b
         {hlg_db_path}

        After running init, you can see the contents of the config
        file by opening it in a text editor, or, better yet, you can
        dump it and get some more help with dob:

         \b
         {codehi}{rawname} config dump{reset}

        {_hint_sqlite}
        """.strip().format(
            default_config_path=highlight_value(default_config_path()),
            hlg_db_path=highlight_value(controller.config['db.path']),
            _hint_sqlite=_hint_sqlite,
            **common_format()
        )
    )
    return _help


# ***
# *** [CONFIG] Commands help.
# ***

def CONFIG_GROUP_HELP(ctx):
    _help = _(
        """
        Commands for managing user configurable values.

        Some application behavior can be changed via config values.

        Config values can be persisted across invocation in a config
        file.

        You can also specify config values at runtime on the command line,
        or using environment variables.

        {underlined}Config File Location{reset}

        By default, {rawname} looks for a configuration file at:

            {default_config_path}

        - You can specify an alternative file location
        using the {codehi}{envkey}{reset} environment value.

          E.g., you could set the environment for just the command subshell like:

          \b
          {codehi}{envkey}=path/to/{rawname}.conf {rawname} COMMAND ...{reset}

          or you could export the environment variable first and then invoke {rawname}:

          \b
          {codehi}export {envkey}=path/to/{rawname}.conf{reset}
          {codehi}{rawname} COMMAND ...{reset}

        - You can alternatively specify the configuration file location
        using the {codehi}-C/--configfile{reset} global option, e.g.,
        using shorthand:

          \b
          {codehi}{rawname} -C path/to/{rawname}.conf COMMAND ...{reset}

          or using --option=value longhand:

          \b
          {codehi}{rawname} --configfile=path/to/{rawname}.conf COMMAND ...{reset}

        {underlined}Config Value Precedence{reset}

        - If no config value is specified for a setting, {rawname}
        uses a default value.

        - If a config value is found in the config value, that value
        takes precedence over the default value.

        - If a corresponding environment variable for the config value
        is found, that value is preferred over the value from the file.

          - The environment variable for each setting is formed from
        a prefix, {codehi}DOB_CONFIG_{reset}, followed by the uppercase
        section name and the uppercase setting name.

          E.g., here's how to specify the db.engine setting using its
        environment variable:

          \b
          {codehi}DOB_CONFIG_DB_ENGINE=sqlite {rawname} stats{reset}

        - If a config value is specified via the command line, that value is
        preferred over all other values.

          - You can specify config values using the {codehi}-c/--config{reset}
        option, e.g.,

          \b
          {codehi}{rawname} -c db.engine=sqlite stats{reset}

        {underlined}Config Command Overview{reset}

          - You can edit the config file directly, or (better yet) you can
        use the {codehi}dob set{reset} command to change its values.
        E.g., to enable coloring whenever you use {rawname}, run:

          \b
          {codehi}{rawname} config set client term_color True{reset}

          or omit the section name (because {rawname} is smart) and run instead:

          \b
          {codehi}{rawname} config set term_color True{reset}

          - If you remove the config file, or if you delete values from it,
        don't worry, {rawname} will use default values instead.

          - You can recreate the config file (and overwrite the existing file)
        with defaults by:

          \b
          {codehi}{rawname} config create --force{reset}

          - The best way to learn about all configurable settings is to
        print the config table, which includes a helpful message for each
        option:

          \b
          {codehi}{rawname} config dump{reset}

          - If you think your config file is missing values, you can
        update it with missing settings by running (naturally) the
        update command:

          \b
          {codehi}{rawname} config update{reset}

            - But you should not care about the contents of the config file
        if you stick to using {codehi}{rawname} config dump{reset} and
        {codehi}{rawname} config set{reset} commands.

            - Although you might care about the config file contents if you'd
        like to add comments to it, which is supported.
        """.format(
            default_config_path=highlight_value(default_config_path()),
            envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
            **common_format()
        )
    )
    return _help


CONFIG_CREATE_HELP = _(
    """
    Writes a new configuration file populated with default values.

    You can overwrite an existing configuration file using --force.
    """
)


CONFIG_CREATE_FORCE_HELP = _(
    """
    If specified, overwrite config file if is exists.
    """
)


CONFIG_DUMP_HELP = _(
    """
    Prints a list of configurable settings, including names, values, and help.
    """
)


CONFIG_GET_HELP = _(
    """
    Prints a configuration value from the config file.
    """
)


CONFIG_SET_HELP = _(
    """
    Writes a configuration value to the config file.
    """
)


CONFIG_UPDATE_HELP = _(
    """
    Write missing configuration values to the config file.
    """
)


# ***
# *** [STORE] Commands help.
# ***

STORE_GROUP_HELP = _(
    """
    Commands for managing the database file.
    """
)


STORE_CREATE_HELP = _(
    """
    Creates an empty database file.

    You can overwrite an existing database file using --force.
    """
)


STORE_CREATE_FORCE_HELP = _(
    """
    If specified, recreate data store if is exists.
    """
)


STORE_PATH_HELP = _(
    """
    Prints the database path.
    """
)


STORE_URL_HELP = _(
    """
    Prints the database URL.
    """
)


STORE_UPGRADE_LEGACY_HELP = _(
    """
    Migrates a legacy “Hamster” database to dob.
    """
)


STORE_UPGRADE_FORCE_HELP = _(
    """
    If specified, overwrite data store if is exists.
    """
)


# ***
# *** [STATS] Commands help.
# ***

STATS_HELP = _(
    """
    Prints stats about your data store.
    """
)


# ***
# *** [LIST] Commands help.
# ***

LIST_GROUP_HELP = _(
    """
    Prints facts, activities, categories, or tags.
    """
)


LIST_ACTIVITIES_HELP = _(
    """
    Prints all activities. Provide optional filtering by name.

    Prints all matching activities one per line.

    SEARCH: String to be matched against activity name.
    """
)


LIST_CATEGORIES_HELP = _(
    """
    Prints all existing categories, ordered by name.
    """
)


LIST_TAGS_HELP = _(
    """
    Prints all tags.
    """
)


LIST_FACTS_HELP = _(
    """
    Prints facts within a date range.

    Matching facts will be printed in a tabular representation.

    TIME_RANGE: Only fact within this time range will be considered.
    """
)


SEARCH_HELP = _(
    """
    Finds facts matching a search term, time range and other options.

    You may use the SEARCH_TERM to find Facts with descriptions
    that contain the SEARCH_TERM.

    You may use the --since and --until options to restrict the
    search to a specific time range.

    You may use the --activity and --category options to restrict
    the search to specific activity and category names.
    """
)


# ***
# *** [USAGE] Commands help.
# ***

USAGE_GROUP_HELP = _(
    """
    Prints activity, category, or tag usage.
    """
)


USAGE_ACTIVITIES_HELP = _(
    """
    Prints all activities and their usage counts.
    """
)


USAGE_CATEGORIES_HELP = _(
    """
    Prints all categories and their usage counts.
    """
)


USAGE_TAGS_HELP = _(
    """
    Prints all tags by usage.
    """
)


USAGE_FACTS_HELP = _(
    """
    Prints all facts by usage.
    """
)


# ***
# *** [CURRENT-FACT] Commands help.
# ***

STOP_HELP = _(
    # Not DRY: Copied from first line of ADD_FACT_THEN.
    """
    Stops active Fact, ending it now or at the time specified.
    """
)


CANCEL_HELP = _(
    """
    Discards the active Fact.
    """
)


CURRENT_HELP = _(
    """
    Prints the active Fact, if there is one.
    """
)


def NO_ACTIVE_FACT_HELP(ctx):
    _help = _(
        """
        No active Fact. Try {italic}starting{reset} a new Fact first.
        """
    ).strip().format(**common_format())
    return _help


def NOTHING_TO_STOP_HELP(ctx):
    _help = _(
        # It doesn't look like there's any current Fact {}to{} stop.
        """
        Sorry, bud, there's no active Fact {italic}to{reset} stop.
        """
    ).strip().format()
    return _help


LATEST_HELP = _(
    """
    Prints latest completed Fact (Fact with most recent end time).
    """
)


HELP_CMD_SHOW = _(
    """
    Prints the active Fact if exists, otherwise the latest Fact.
    """
)


# ***
# *** [ADD-FACT] Commands help.
# ***

def ADD_FACT_REFERRAL():
    _help = _(
        """
        For more help on this and the other Add Fact commands, try

          {codehi}{rawname} --pager help add{reset}
        """.strip().format(**common_format())
    )
    return _help


# verify_none
ADD_FACT_ON = _(
    """
    Aliases the 'now' command, e.g., `dob on act@gory #tag: Blah...`.
    """
)


# verify_none
ADD_FACT_NOW = _(
    # FIXME/2019-11-22: (lb): I think "if nothing active" might be wrong.
    """
    Starts a new Fact if nothing active, using time now.
    """
)


# verify_none
ADD_FACT_START = _(
    # Not DRY: Copied from first line of ADD_FACT_AT.
    """
    Starts new Fact, beginning now or at the time specified.
    """
)


# verify_start
def ADD_FACT_AT(ctx):
    _help = _(
        """
        \b
        Starts new Fact, beginning now or at the time specified.

        \b
        Might also stop the current ongoing fact if one exists and the
        new fact starts after the current fact; or might change the stop
        time of an existing fact if the two facts' time windows overlap.

        {}
        """
    ).format(ADD_FACT_REFERRAL())
    return _help


# verify_then
ADD_FACT_THEN = _(
    """
    Stops active Fact and Starts new, using now or time specified.

    Ends active Fact and Starts new Fact, at now or offset.

    Starts Fact, at time now or optional offset, ending active Fact.

    Starts Fact, ending active Fact, using now or optional offset.

    This is basically a shortcut for the at command, which requires a time
    offset, e.g.,

      {rawname} then Grinding beans for coffee.

    is the same as:

      {rawname} at +0: Grinding beans...

    FIXME: Verify the colon...
    If you want to specify an offset, you can, just use a colon,
    which could work well to throw down a gap fact, e.g.,

      {rawname} then -5m: Woke up.
      {rawname} now Grinding beans...

    """
)


# verify_still
ADD_FACT_STILL = _(
    """
    Stops active Fact and Starts new Fact, copying metadata.

    Starts Fact, copying metadata from ending Fact.

    Starts Fact, copying activity, category, and tags from ending Fact.

    Ends active Fact, and starts new Fact, and copies forward metadata.

    Starts the new Fact using the same Act@Gory and Tags (Metadata) as the
    active Fact that is ended.
    """
)


# Note that dob.transcode mentions a `since:` that's like `after:/next:` (verify_after).
# verify_after
def ADD_FACT_AFTER(ctx):
    _help = _(
        """
        Starts new Fact, beginning when the last Fact ended.

        {}
        """.strip().format(ADD_FACT_REFERRAL())
    )
    return _help


# verify_after
ADD_FACT_NEXT = _(
    """
    Aliases the 'after' command, e.g., `dob next: Foo bar...`.
    """
)


# verify_end
ADD_FACT_TO = _(
    """
    Stops active Fact, ending it now or at the time specified.

    Stops the active Fact ending now or at the specified time.
    """
)


# verify_end
ADD_FACT_UNTIL = _(
    """
    Aliases the 'to' command, e.g., `dob until -10m: Yada...`.
    """
)


# verify_both
ADD_FACT_FROM = _(
    """
    Inserts new Fact using the start and end time indicated.

    E.g., {rawname} from 2019-01-01 00:00 to 2019-01-01 01:00: Happy New Year!
    """
)


# ***
# *** [EDIT] Command help.
# ***

# (lb): 2019-11-22: I had been using the term "Carousel" in docs, but I
# think I should call it an "editor", and sometimes an "interactive" one.
EDIT_FACT_HELP = _(
    """
    Runs the interactive Fact editor in your terminal.
    """
)


# ***
# *** [EXPORT] Command help.
# ***

EXPORT_HELP = _(
    """
    Exports facts and other interesting data you desire.
    """
)


# ***
# *** [IMPORT] Command help.
# ***

# FIXME/2018-05-12: (lb): Document hamster-import more fully.
# - This command is quite powerful, and it might be a good way
# to demonstrate how all the dob-on/dob-after/etc. commands work.
IMPORT_HELP = _(
    """
    Imports Facts from a text file using a natural syntax.

    Useful if you cannot use dob for a while but can
    maintain a text file. Or if you need to massage
    data from another source into dob, it's easy to
    prepare an import file that dob can read and use
    to make Facts in the database.
    """
)


# ***
# *** [COMPLETE] Command help.
# ***

COMPLETE_HELP = _(
    """
    Bash tab-completion helper.
    """
)


# ***
# *** [MIGRATE] Commands help.
# ***

MIGRATE_GROUP_HELP = _(
    """
    Upgrades the database after installing a new major release.
    """
)


MIGRATE_CONTROL_HELP = _(
    """
    Marks a database as under version control.
    """
)


MIGRATE_DOWN_HELP = _(
    """
    Downgrades the database version by 1 script.
    """
)


MIGRATE_UP_HELP = _(
    """
    Upgrades the database version by 1 script.
    """
)


MIGRATE_VERSION_HELP = _(
    """
    Shows the database migration version.
    """
)


# ***
# *** [--GLOBAL-OPTIONS] Global Options help. [run_cli.py]
# ***

GLOBAL_OPT_VERBOSE = _(
    """
    Be chatty. (-VV for more.)
    """
)


GLOBAL_OPT_VERBOSER = _(
    """
    Be chattier.
    """
)


GLOBAL_OPT_COLOR_NO_COLOR = _(
    """
    Color, or plain. (Default: Auto.)
    """
)


GLOBAL_OPT_PAGER_NO_PAGER = _(
    """
    Send output to pager, or not. (Default: No.)
    """
)


GLOBAL_OPT_CONFIG = _(
    """
    Override config setting(s) (may do multiple).
    """
)


GLOBAL_OPT_CONFIGFILE = _(
    """
    Alternative path to configuration file.
    """
)

