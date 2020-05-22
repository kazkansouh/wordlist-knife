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

import wordlistknife.config as C
from pathlib import Path

name = 'wordlist-knife'
version = '0.0.1'
encoding = 'utf8'
strip_chars = '\n\r'
line_end = '\n'
word_concat = ['', '-', '_']
store = C.ConfigFile(Path.home().joinpath('.wordlist-knife'))
