# Copyright (C) 2020 Karim Kanso. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wordlistknife as wk
import functools
import re

def loadupper(arg):
    if len(arg):
        return None
    return lambda x: x.upper()

def loadlower(arg):
    if len(arg):
        return None
    return lambda x: x.lower()

def loadsubst(arg):
    if len(arg) < 3 or len(arg[2:].split(arg[1], 1)) != 2:
        raise ValueError(
            'subst should be of the form "subst:<del><pat><del><subst>"'
        )

    pat, repl = arg[2:].split(arg[1], 1)
    return  lambda x: re.sub(pat, repl, x)

__manglers={
    'upper': {
        'func': loadupper,
        'desc': 'Convert words to uppercase.',
    },
    'lower': {
        'func': loadlower,
        'desc': 'Convert words to lowercase.',
    },
    'subst': {
        'func': loadsubst,
        'desc': ''' \

        Regex substitution, first char is delimiter. e.g. to prefix
        php pages with "x_" the following could be used:
        "subst:/^([^.]+)\.php/x_\1.php".  ''',
    },
}

def manglers():
    return { i: __manglers[i]['desc'] for i in __manglers }

def mangler(arg):
    for k in __manglers:
        if arg.startswith(k):
            m = __manglers[k]['func'](arg[len(k):])
            if m:
                return m
            else:
                break
    raise ValueError('unknown mangler: {}'.format(arg))

def compile(args):
    if not args:
        return None
    return functools.reduce(
        lambda a, b: lambda x: b(a(x)),
        map(mangler, args or [])
    )
