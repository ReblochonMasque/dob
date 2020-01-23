#!/usr/bin/env python

# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma
# Copyright © 2015-2016 Eric Goller
# All  rights  reserved.
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

"""
Packaging instruction for setup tools.

Refs:

  https://setuptools.readthedocs.io/

  https://packaging.python.org/en/latest/distributing.html

  https://github.com/pypa/sampleproject
"""

from setuptools import find_packages, setup

# *** Package requirements.

requirements = [
    # Nice! Because Click was already halfway there... just not quite.
    # https://github.com/jonathaneunice/ansiwrap
    # (lb): I considered adding this to Click, but Click has no dependencies!
    #       So let's keep it pure.
    'ansiwrap >= 0.8.4',
    # Platform-specific directory magic.
    #  https://github.com/ActiveState/appdirs
    'appdirs',
    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    'click--hotoffthehamster',
    # Indispensable aliases support for Click.
    #  Stolen from: https://github.com/click-contrib/click-aliases
    #  Released at: https://github.com/hotoffthehamster/click-alias
    'click-alias >= 0.1.0a1',
    # Enable Click color support (we don't use colorama directly, but it does),
    #  "on Windows, this ... is only available if colorama is installed".
    #  https://click.palletsprojects.com/en/5.x/utils/#ansi-colors
    #  https://pypi.org/project/colorama/
    'colorama',
    # INI/config parser, even better (preserves comments and ordering).
    #  https://github.com/DiffSK/configobj
    #  https://configobj.readthedocs.io/en/latest/
    'configobj >= 5.0.6',
    # Compatibility layer between Python 2 and Python 3.
    #  https://python-future.org/
    'future',
    # Vocabulary word pluralizer.
    #  https://github.com/ixmatus/inflector
    'Inflector',
    # Humanfriendly is one of the many table formatter choices.
    #  https://github.com/xolox/python-humanfriendly
    'humanfriendly',
    # Elapsed timedelta formatter, e.g., "1.25 days".
    'human-friendly_pedantic-timedelta >= 0.0.6',  #  Imports as pedantic_timedelta.
    # https://github.com/mnmelo/lazy_import
    'lazy_import',
    # The heart of Hamster. (Ye olde `hamster-lib`).
    'nark',
    # Amazeballs prompt library.
    # FIXME/2019-02-21: Submit PR. Until then, whose fork?
    'prompt-toolkit-dob >= 2.0.9',  # Imports as prompt_toolkit.
    # Just Another EDITOR package.
    #  https://github.com/fmoo/python-editor
    'python-editor',  # Imports as editor.
    # Virtuous Six Python 2 and 3 compatibility library.
    #  https://six.readthedocs.io/
    'six',
    # Tabulate is one of the many table formatter choices.
    #  https://bitbucket.org/astanin/python-tabulate
    'tabulate',
    # Texttable is one of the many table formatter choices.
    #  https://github.com/bufordtaylor/python-texttable
    'texttable',
]

# *** Minimal setup() function -- Prefer using config where possible.

# (lb): All settings are in setup.cfg, except identifying packages.
# (We could find-packages from within setup.cfg, but it's convoluted.)

setup(
    install_requires=requirements,
    packages=find_packages(exclude=['tests*']),
    # Tell setuptools to determine the version
    # from the latest SCM (git) version tags.
    #
    # Without the following two lines, e.g.,
    #   $ python setup.py --version
    #   3.0.0a31
    # But with 'em, e.g.,
    #   $ python setup.py --version
    #   3.0.0a32.dev3+g6f93d8c.d20190221
    # Or, if the latest commit is tagged,
    # and your working directory is clean,
    # then the version reported (and, e.g.,
    # used on make-dist) will be from tag.
    # Ref:
    #   https://github.com/pypa/setuptools_scm
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

