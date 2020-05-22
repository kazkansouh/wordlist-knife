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
import os

class ConfigFile:
    """
    Defines a simple file format that consists of lines like:

      tag:filepath

    In addition, '//' are accepted as comments.
    """
    __data = {}

    def __init__(self, fname):
        try:
            with open(fname, 'r', encoding='utf8') as conf:
                for l in [
                        j for l in conf
                          for j in [ l.split('//', 1)[0].strip() ]
                          if j
                ]:
                    l = l.split(':', 1)
                    if len(l) != 2:
                        print('warning: invalid line in config file',
                              file=sys.stderr)
                        continue
                    if not os.path.isfile(l[1]):
                        print('warning: file {} in config does not exist'
                              .format(l[1]),
                              file=sys.stderr)
                        continue
                    self.__data[l[0]] = l[1]
        except FileNotFoundError:
            pass

    def __getitem__(self, i): return self.__data.__getitem__(i)
    def __contains__(self, i): return self.__data.__contains__(i)
    def __iter__(self): return self.__data.__iter__()
