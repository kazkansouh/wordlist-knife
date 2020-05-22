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
import itertools
import operator
import functools
import re

def loadfile(arg):
    with open(arg, 'r', encoding=wk.encoding) as wl:
        return map(lambda x: x.strip(wk.strip_chars), wl.readlines())

def loadlist(arg):
    if len(arg) < 2:
        raise ValueError('list should be of the form "list:<del><it><del><it>"')
    delim = arg[0]
    return arg[1:].split(delim)

def fancyword(word):
    return list(dict.fromkeys([
        word,
        word.upper(),
        word.lower(),
        word.capitalize(),
    ]))

def loadfancy(arg):
    srcwords = list(loadlist(arg))
    words = []

    for l in range(len(srcwords)):
        for p in itertools.permutations(srcwords, l+1):
            packed_words = [ fancyword(w) for w in p ]
            packed_words = itertools.chain(
                *zip(packed_words, [wk.word_concat]*len(packed_words)))
            packed_words = list(packed_words)[:-1]
            for w in itertools.product(*packed_words):
                words.append(functools.reduce(operator.concat, w, ""))
    return words


__preload_lists={
    'apache': [
        re.compile('\\.phps$'),
        re.compile('(^|/)\\.ht'),
    ]
}

def preload_lists():
    preload = {
        k: [
            v if type(v)==str else (v.pattern + ' (regex)')
            for v in __preload_lists[k]
        ]
        for k in __preload_lists
    }

    for l in wk.store:
        if not l in preload:
            preload[l] = wk.store[l] + ' (file)'

    return preload

def saveload(arg):
    if arg in __preload_lists:
        return __preload_lists[arg]

    if arg in wk.store:
        return loadfile(wk.store[arg])

    return None

__processors={
    'file': {
        'func': loadfile,
        'desc': 'Read a wordlist file from path.',
    },
    'list': {
        'func': loadlist,
        'desc': (
            'Define constant list, first char is delimiter. '+
            'e.g. list:/abc/123. Useful for quickly adding/removing'+
            ' a few words to a wordlist.'
        ),
    },
    'fancy': {
        'func': loadfancy,
        'desc': '''
            Generate variants of list with upper/lower/title cases.
            Same format as list. Useful for deriving a number of words from
            a small number of known words, e.g. a company name or a person.
            Given as: "fancy:/jo/bloggs" to generate variants.
        ''',
    },
    'save': {
        'func': saveload,
        'desc': '''

            Pre-configured lists, e.g. save:apache.  These are either
            hardcoded (such as apache) and typically for use with with
            --filters, or read from the ~/.wordlist-knife file as
            aliases for wordlist paths. This file should consist of
            lines such as "mywordlist:/path/to/wordlist", then this
            wordlist can be used as "save:mywordlist".

        ''',
    },
}

def processors():
    return { i: __processors[i]['desc'] for i in __processors }

def wordlist(arg):
    try:
        return loadfile(arg)
    except FileNotFoundError:
        pass

    for k in __processors:
        if arg.startswith(k + ':'):
            return __processors[k]['func'](arg[len(k)+1:])
    return None

def filter(arg):
    f = wordlist(arg)
    if f: return f

    if not arg.startswith('regex:') or len(arg) < 7:
        return None

    return re.compile(arg[6:])
