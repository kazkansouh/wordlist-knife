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

def build(wordlists):
    seen = {}
    words = []
    other = []
    for wl in wordlists:
        if type(wl) != list and type(wl) != map:
            other.append(wl)
            continue
        for w in wl:
            if type(w) != str:
                other.append(w)
                continue
            if seen.get(w) == None:
                words.append(w)
                seen[w] = 1
    return (words, other)

def subtract(wordlist, filt_fixed, filt_regexes):
    def f(x):
        if x not in filt_fixed:
            for r in filt_regexes:
                if r.search(x):
                    return False
            return True
        return False

    return filter(f , wordlist)
