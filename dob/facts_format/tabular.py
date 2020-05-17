# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

from collections import namedtuple

from gettext import gettext as _

from dob_bright.termio.ascii_table import generate_table

__all__ = (
    'generate_facts_table',
    'output_ascii_table',
)


def output_ascii_table(
    controller,
    results,
    show_usage=False,
    hide_duration=False,
    chop=False,
    table_type='friendly',
):
    def _output_ascii_table():
        table, headers = generate_facts_table(
            controller,
            results,
            show_duration=not hide_duration,
            show_usage=show_usage,
        )
        # 2018-06-08: headers is:
        #   ['Key', 'Start', 'End', 'Activity', 'Category', 'Tags', 'Description',]
        #   and sometimes + ['Duration']
        desc_col_idx = 6  # MAGIC_NUMBER: Depends on generate_facts_table.
        # FIXME: (lb): This is ridiculously slow on a mere 15K records! So
        #   Use --limit/--offset or other ways of filter filter
        #   We should offer a --limit/--offset feature.
        #   We could also fail if too many records; or find a better library.
        generate_table(table, headers, table_type, truncate=chop, trunccol=desc_col_idx)
        logger_warn_if_truncated(controller, len(results), len(table))

    def logger_warn_if_truncated(controller, n_results, n_rows):
        if n_results > n_rows:
            controller.client_logger.warning(_(
                'Too many facts to process quickly! Found: {} / Shown: {}'
            ).format(format(n_results, ','), format(n_rows, ',')))

    _output_ascii_table()

# ***

def generate_facts_table(controller, facts, show_duration=True, show_usage=False):
    """
    Create a nice looking table representing a set of fact instances.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances representing a single fact.
    """
    show_duration = show_duration or show_usage

    # If you want to change the order just adjust the dict.
    headers = {
        'key': _("Key"),
        'start': _("Start"),
        'end': _("End"),
        'activity': _("Activity"),
        'category': _("Category"),
        'tags': _("Tags"),
        'description': _("Description"),
    }
    columns = [
        'key',
        'start',
        'end',
        'activity',
        'category',
        'tags',
        'description',
    ]

    if show_duration:
        headers['delta'] = _("Duration")
        columns.append(_('delta'))

    header = [headers[column] for column in columns]

    TableRow = namedtuple('TableRow', columns)

    table = []

    n_row = 0
    # FIXME: tabulate is really slow on too many records, so bail for now
    #        rather than hang "forever", man.
    # 2018-05-09: (lb): Anecdotal evidence suggests 2500 is barely tolerable.
    #   Except it overflows my terminal buffer? and hangs it? Can't even
    #   Ctrl-C back to life?? Maybe less than 2500. 1000 seems fine. Why
    #   would user want that many results on their command line, anyway?
    #   And if they want to process more records, they might was well dive
    #   into the SQL, or run an export command instead.
    row_limit = 1001

    for fact in facts:

        if not show_usage and not group_by_specified:
            # It's tuple: the Fact, the count, and the duration (aka span).
            #  _span = fact[2]  # Should be same/similar to what we calculate.
            # The count column was faked (static count), so the table
            # has the same columns as the act/cat/tag usage tables.
            assert fact[1] == 1
            fact = fact[0]

        n_row += 1
        if n_row > row_limit:
            break

        if fact.category:
            category = fact.category.name
        else:
            category = ''

        if fact.tags:
            tags = '#'
            tags += '#'.join(sorted([x.name + ' ' for x in fact.tags]))
        else:
            tags = ''

        if fact.start:
            fact_start = fact.start.strftime('%Y-%m-%d %H:%M')
        else:
            fact_start = _('<genesis>')
            controller.client_logger.warning(_('Fact missing start: {}').format(fact))

        if fact.end:
            fact_end = fact.end.strftime('%Y-%m-%d %H:%M')
        else:
            # FIXME: This is just the start of supporting open ended Fact in db.
            fact_end = _('<active>')
            # So that fact.delta() returns something.
            fact.end = controller.now

        additional = {}
        if show_duration:
            additional['delta'] = fact.format_delta(style='')

        table.append(
            TableRow(
                key=fact.pk,
                activity=fact.activity.name,
                category=category,
                description=fact.description or '',
                tags=tags,
                start=fact_start,
                end=fact_end,
                **additional,
            )
        )

    return (table, header)

