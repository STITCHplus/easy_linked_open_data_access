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

from backend import Backend

__all__ = ["Geonames"]

__author__ =    "Willem Jan Faber <wjf@fe2.nl>"
__version__ =   "1.0"
__date__ =      "2011-11-15"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__ =   "GNU GPL"

app_name = "geonames"

class Geonames(Backend):
    '''Geonames a easy to use library to get a geonames record, cache and parse it.
Usage: geonames.py <geonames_identifier> 
    ''' 
    #% globals()

    URL_GEONAMES = "http://ws.geonames.org/searchJSON?q=%s"

    def __init__(self, *fargs, **args):
        Backend.__init__(self, *fargs, **args)

        if "log_path" in args:
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
        for geonames_identifier in self.request:
            self._get_geonames_record(geonames_identifier)

    def set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)

    def _get_geonames_record(self, geonames_identifier):
        if self.debug:
            self.log.info("getting.. %s " % (geonames_identifier))
        if geonames_identifier.lower().find("http") > -1:
            if geonames_identifier.find('http:/') > -1:
                geonames_identifier = geonames_identifier.split('/')[-1].strip()
            elif geonames_identifier.find('%2F') > -1:
                geonames_identifier = geonames_identifier.split('%2F')[-1].strip()
        if geonames_identifier.lower().startswith("dbp:") or geonames_identifier.lower().startswith("geonames:"):
            geonames_identifier = geonames_identifier.split(':')[0]

        url = self.URL_GEONAMES % geonames_identifier.strip()
        data = self.get(url)

        if not data:
            if self.debug:
                self.log.info("No geonames data for: %s @ %s (via %s)" % (geonames_identifier, url, self.backend))
        else:
            try:
                self[data["geonames"][0]["toponymName"]] = data["geonames"][0]
            except:
                pass

def _usage(stream):
    stream.write(Geonames.__doc__ + "\n")

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
        fb = Geonames(args,debug=True,log_path="/tmp")
        fb.execute()
        pprint(fb)
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
