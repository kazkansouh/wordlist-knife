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
import wordlistknife.input as I
import wordlistknife.mangle as M
import re
from collections.abc import Iterable

def build(wordlists, wordsonly=True, mangler=None):
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
            if mangler:
                w = mangler(w)
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

    return filter(f, wordlist)

def assemblewordlist(wordlists_spec, filters_spec, manglers_spec):
    wordlists = []
    for wl in wordlists_spec:
        wordlist = I.wordlist(wl)
        if not wordlist:
            raise ValueError('bad wordlist argument: {}'.format(wl))
        wordlists.append(wordlist)

    filters = []
    for f in filters_spec or []:
        filt = I.filter(f)
        if not filt:
            raise ValueError('bad filter argument: {}'.format(f))
        filters.append(filt)

    mangler = M.compile(manglers_spec)

    return subtract(build(wordlists, mangler=mangler),
                    build(filters, wordsonly=False))
