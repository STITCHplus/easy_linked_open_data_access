#!/usr/bin/env python
# -*- coding: utf-8 -*-

## 
## Copyright (C) 2011-2012 National library of the Netherlands, Willem Jan Faber <willemjanfaber@fe2.nl>.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139,
## USA.
##

import os
import sys
import time

try:
    import json
except:
    import simplejson as json

from backend import Backend

__all__ = ["Freebase"]

__author__ =    "Willem Jan Faber <wjf@fe2.nl>"
__version__ =   "1.0"
__date__ =      "2011-11-15"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__ =   "GNU GPL"

app_name = "freebase"

class Freebase(Backend):
    '''Freebase a easy to use library to get a freebase record, cache and parse it.
Usage: freebase.py <freebase_identifier> 
    ''' 
    #% globals()

    URL_FREEBASE = "http://api.freebase.com/api/experimental/topic/extended?id=%s&domains=all"

    def __init__(self, *fargs, **args):
        Backend.__init__(self, *fargs, **args)
        self.log_path = None
        if "log_path" in args:
            self.log_path = args["log_path"]
            if "debug" in args:
                self.debug = args["debug"]
            else:
                self.debug = True
        else:
            self.debug = False

        if self.debug:
            self.setup_logfile(app_name, args["log_path"])

        if "backend" in args:
            self.set_backend(args["backend"])
        else:
            self.set_backend(self.default_backend)
        
        if len(fargs) > 1:
            if type(fargs[0]) == str:
                self.request = fargs
            else:
                print('fixme', fargs)
                sys.exit()
        else:
            self.request = fargs
        if type(self.request)  == tuple:
            self.request = self.request[0]

    def execute(self):
        for freebase_identifier in self.request:
            self._get_freebase_record(freebase_identifier)

    def set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)


    def _get_freebase_record(self, freebase_identifier):
        if self.debug:
            self.log.info("getting.. %s " % (freebase_identifier))
        if freebase_identifier.lower().find("http") > -1:
            if freebase_identifier.find('http:/') > -1:
                freebase_identifier = freebase_identifier.split('/')[-1].strip()
            elif freebase_identifier.find('%2F') > -1:
                freebase_identifier = freebase_identifier.split('%2F')[-1].strip()
        if freebase_identifier.lower().startswith("dbp:") or freebase_identifier.lower().startswith("freebase:"):
            freebase_identifier = freebase_identifier.split(':')[0]

        url = self.URL_FREEBASE % freebase_identifier.strip()
        data = self.get(url)

        if not data:
            if self.debug:
                self.log.info("No Freebase data for: %s @ %s (via %s)" % (freebase_identifier, url, self.backend))
        else:
            try:
                self[freebase_identifier] = json.loads(data)
                self[freebase_identifier] = self[freebase_identifier][freebase_identifier]["result"]
                if "thumbnail" in self[freebase_identifier]:
                    self[freebase_identifier]["thumbnail"]+="?maxheight=200&mode=fit&maxwidth=150"
            except:
                try:
                    self[freebase_identifier] = data
                    self[freebase_identifier] = self[freebase_identifier][freebase_identifier]["result"]
                    if "thumbnail" in self[freebase_identifier]:
                        self[freebase_identifier]["thumbnail"]+="?maxheight=200&mode=fit&maxwidth=150"
                except:
                   return(False)

def _usage(stream):
    stream.write(Freebase.__doc__ + "\n")

def main(arguments):
    from pprint import pprint
    import getopt
    try:
        opts, args = getopt.getopt(arguments, app_name+":", ["help", "version", "license"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-l", "--license"):
            sys.stdout.write(__licence__)
            sys.exit(0)
        if opt in ("-h", "--help"):
            _usage(sys.stdout)
            sys.exit(0)
        if opt in ("-v", "--version"):
            sys.stdout.write(__version__)
            sys.exit(0)

    query = "".join(args)

    if query != "":
        fb = Freebase(args,debug=True)
        fb.execute()
        pprint(fb)
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
