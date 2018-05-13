# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from collections import namedtuple

import click


__all__ = ['generate_facts_table', 'list_current_fact']


def list_current_fact(controller):
    """
    Return current *ongoing fact*.

    Returns:
        None: If everything went alright.

    Raises:
        click.ClickException: If we fail to fetch any *ongoing fact*.
    """
    try:
        fact = controller.facts.get_tmp_fact()
    except KeyError:
        message = _(
            "There seems no be no activity beeing tracked right now."
            " maybe you want to *start* tracking one right now?"
        )
        raise click.ClickException(message)
    else:
        fact.end = datetime.datetime.now()
        string = '{fact} ({duration} minutes)'.format(fact=fact, duration=fact.get_string_delta())
        click.echo(string)


def generate_facts_table(facts):
    """
    Create a nice looking table representing a set of fact instances.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances representing a single fact.
    """
    # If you want to change the order just adjust the dict.
    headers = {
        'key': _("Key"),
        'start': _("Start"),
        'end': _("End"),
        'activity': _("Activity"),
        'category': _("Category"),
        'tags': _("Tags"),
        'description': _("Description"),
        'delta': _("Duration")
    }

    columns = (
        'key', 'start', 'end', 'activity', 'category', 'tags', 'description', 'delta',
    )

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
            fact_start = '<genesis>'
            controller.client_logger.warning(_('Fact missing start: {}').format(fact))

        if fact.end:
            fact_end = fact.end.strftime('%Y-%m-%d %H:%M')
        else:
            # FIXME: This is just the start of supporting open ended Fact in db.
            fact_end = '<ongoing>'
            # So that fact.delta() returns something.
            fact.end = datetime.datetime.now()

        # [TODO]
        # Use ``Fact.get_string_delta`` instead!
        fact_delta = (
            '{minutes} min.'.format(minutes=(int(fact.delta.total_seconds() / 60)))
        )

        table.append(
            TableRow(
                key=fact.pk,
                activity=fact.activity.name,
                category=category,
                description=fact.description,
                tags=tags,
                start=fact_start,
                end=fact_end,
                delta=fact_delta,
            )
        )

    return (table, header)

