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
import json

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
                self.__data = json.loads(conf.read())

            for k in list(self.__data):
                if 'wordlists' not in  self.__data[k]:
                    print(
                        '[W] list {} in config has no wordlists'.format(k),
                        file=sys.stderr
                    )
                    del self.__data[k]
                    continue
                if 'filters' not in self.__data[k]:
                    self.__data[k]['filters'] = None
                if 'manglers' not in self.__data[k]:
                    self.__data[k]['manglers'] = None

                if 'desc' not in self.__data[k]:
                    if len(self.__data[k]['wordlists']) == 1:
                        self.__data[k]['desc'] = self.__data[k]['wordlists'][0]
                    else:
                        self.__data[k]['desc'] = 'complex user defined list'

        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            print(
                '[W] unable to parse config file',
                file=sys.stderr
            )

    def __getitem__(self, i): return self.__data.__getitem__(i)
    def __contains__(self, i): return self.__data.__contains__(i)
    def __iter__(self): return self.__data.__iter__()
