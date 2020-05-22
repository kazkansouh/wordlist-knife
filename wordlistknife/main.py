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

import sys
import argparse
import wordlistknife as wk
import wordlistknife.input as I
import wordlistknife.builder as B
import wordlistknife.mangle as M
import textwrap
import functools

class WordlistKnifeHelpFormatter(argparse.HelpFormatter):
    """Format blocks of text by paragraphs.
    Based on implementation based on:
    https://github.com/python/cpython/blob/master/Lib/argparse.py

    Makes use of internal api to argparse, but appears to work.
    """

    def _fill_text(self, text, width, indent):
        text = text.strip()
        lines = ""
        for line in text.split('\n\n'):
            line = self._whitespace_matcher.sub(' ', line).strip()
            lines += textwrap.fill(
                line,
                width,
                initial_indent=indent + "  ",
                subsequent_indent=indent
            ) + '\n\n'
        return lines

    def _split_lines(self, text, width):
        text=text.strip()
        lines = []
        for line in text.split('\n\n'):
            line = self._whitespace_matcher.sub(' ', line).strip()
            lines += textwrap.wrap(line, width) + ['']
        return lines

def main():
    parser = argparse.ArgumentParser(description=textwrap.dedent('''

    Tool for mangling wordlists. Works by reading in one ore more
    source wordlists, removing duplicates entries and then filtering
    the words. When the words are output, the original order is
    preserved (with exception of removed entries). Also has support
    for basic wordlist generation from keywords.

    Can be used in number of ways from merging wordlists, or just
    appending new words to an existing wordlist, filtering existing
    wordlists or supplementing wordlists with keywords (and some
    derivations).

    Currently there is no support for sorting, as its often preferable
    to have wordlists start with common words.

    '''),
    epilog='''
    {} v{}.
    Copyright (C) 2020 Karim Kanso. All Rights Reserved.
    '''.format(wk.name, wk.version),
    formatter_class=WordlistKnifeHelpFormatter,
    )
    parser.add_argument(
        'wordlists',
         help=textwrap.dedent('''

         Source wordlists. These must occur before the "--filters"
         argument, if used, otherwise argparse can not determine where
         the parameters belong. These arguments can be paths to
         wordlist files or specifications of wordlists to generate.

         Each argument is processed as follows: First, it is check to
         determine if its a file that can be opened. If so, its opened
         and the lines are used. Otherwise it will be interpreted as
         "tag:value" where the tag determines the meaning of the
         value. The following tags are supported:

         {}

         The following lists are predefined (i.e. for use with save):

         {}

         '''.format(functools.reduce(
             lambda x, y: '* {}: {}\n\n'.format(y, I.processors()[y]) + x,
             I.processors(),
             ''
         ), functools.reduce(
             lambda x, y : '* {}: {}\n\n'.format(
                 y,
                 I.preload_lists()[y] if type(I.preload_lists()[y]) == str else
                 functools.reduce(
                     lambda i, j: '{}, {}'.format(j, i),
                     I.preload_lists()[y])) + x,
             I.preload_lists(),
             ''
         ))),
        type=str,
        nargs='+',
        metavar='LIST'
    )
    parser.add_argument(
        '--filters',
        help=textwrap.dedent('''

        Items of the filter argument are removed from the source
        wordlists. Each filter follows the same rules as the
        wordlists, i.e. can be a file or specified with a tag.

        However, in addition, it also supports the "regex" tag that
        filters the words based on a given
        regex. E.g. "regex:\\.phps$".

        '''),
        type=str,
        nargs='+',
        metavar='FILT'
    )
    parser.add_argument(
        '--manglers',
        help=textwrap.dedent('''

        Mangle (i.e. mutate) words. Each mangler is applied in order
        given on command line.

        The following manglers are supported:

        {}

        '''.format(functools.reduce(
             lambda x, y: '* {}: {}\n\n'.format(y, M.manglers()[y]) + x,
             M.manglers(),
             ''
        ))),
        type=str,
        nargs='+',
        metavar='MNGL'
    )
    parser.add_argument(
        '--encoding',
        help='''

        Specify the encoding to use for io. E.g. when using
        rockyou.txt it is required to set this to latin1. (default:
        utf8).

        ''',
        type=str,
        metavar='ENC',
        default='utf8',
    )
    parser.add_argument(
        '--fancy-no-empty-concat',
        dest='fancy_non_empty',
        help='Disable joining words with the empty string for fancy.',
        action='store_true',
    )
    parser.add_argument(
        '--fancy-concat-chars',
        dest='fancy_chars',
        type=list,
        help='List of chars to use for joining words for fancy. (default: -_)',
        default='-_',
    )

    args = parser.parse_args()
    wk.encoding = args.encoding
    wk.word_concat = args.fancy_chars
    if not args.fancy_non_empty:
        wk.word_concat.append('')
    if not wk.word_concat:
        raise ValueError("no concat chars for fancy specified")

    for w in B.assemblewordlist(args.wordlists, args.filters, args.manglers):
        try:
            # not sure if this is the best way to write directly to
            # the stdout, but seems to work
            sys.stdout.buffer.raw.write((w + wk.line_end).encode(wk.encoding))
        except BrokenPipeError:
            break

if __name__ == '__main__':
    main()
