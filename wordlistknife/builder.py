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

import re
from collections.abc import Iterable

def build(wordlists, wordsonly=True):
    seen = {}
    other = []
    for wl in wordlists:
        if not isinstance(wl, Iterable):
            other.append(wl)
            continue
        for w in wl:
            if type(w) != str:
                other.append(w)
                continue
            if seen.get(w) == None:
                yield w
                seen[w] = 1
    if not wordsonly:
        for o in other:
            yield o

def subtract(wordlist, filters):
    # store fixed strings in hash map to speed up checks
    fixed_filters = {}
    regex_filters = []
    for filt in filters:
        if type(filt) == str:
            fixed_filters[filt] = True
        elif type(filt) == re.Pattern:
            regex_filters.append(filt)
        else:
            raise TypeError('Invalid type {} in filter list'.format(type(filt)))

    def f(x):
        if not x in fixed_filters:
            for r in regex_filters:
                if r.search(x):
                    return False
            return True
        return False

    return filter(f , wordlist)
