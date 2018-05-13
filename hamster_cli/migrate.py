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


__all__ = ['downgrade', 'upgrade', 'version']


# FIXME/2018-05-10: (lb): Continue wiring migration feature.
#                   None of these are implemented in LIB yet!


def downgrade(controller):
    controller.store.migrations.downgrade()


def upgrade(controller):
    controller.store.migrations.upgrade()


def version(controller):
    controller.store.migrations.version()
