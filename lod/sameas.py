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
import urllib
import lxml_lib

from backend import Backend
import isbn_check

sys.path.append(os.path.dirname(__file__))

import warnings
warnings.filterwarnings("ignore")

__all__         = ["SameAs"]
__author__      = "Willem Jan Faber <willemjan@fe2.nl>"
__version__     = "1.0"
__copyright__   = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__     = "GNU GPL"

program_name = "sameas"

class sameAs(Backend):
    '''SameAs a easy to use library to find information about symantic related tings.
Usage: sameas <URL>
    ''' 
 
 
    URL_SAMEAS = "http://sameas.org/json?uri=%s"
    URL_SAMEASQ = "http://sameas.org/json?q=%s"
    URL_SAMEAS_ISBN = "http://www.librarything.com/api/thingISBN/%s"

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
            self.setup_logfile("sameas", args["log_path"])

        if "backend" in args:
            self._set_backend(args["backend"])
        else:
            self._set_backend(self.default_backend)
        
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
        for sameas in self.request:
            self._sameas(sameas)

    def _set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)
        return(True)

    def _sameas(self, sameas):
        if sameas.startswith('http'):
            url = self.URL_SAMEAS % sameas
            sameas = sameas.replace('http%3A//', 'http://')
            data = self.get(url)
            if type(data) == list:
                for item in data[0]["duplicates"]:
                    if item.find('http://rdf.freebase.com/ns/') > -1:
                        item=item.replace('http://rdf.freebase.com/ns/', 'http://data.kbresearch.nl/fb:/').replace('en.','en/').replace('guid.','guid/')
                    self._add(sameas, item.replace('http://dbpedia.org/resource/','http://data.kbresearch.nl/DBP:'), "same")
            else:
                return(False)
        elif isbn_check.isValid(sameas):
            data = self.get(self.URL_SAMEAS_ISBN % sameas)
            xml = lxml_lib.fromstring(data)
            for item in xml.iterchildren():
                isbn = str(item.text)
                if not sameas == isbn and not sameas == isbn_check.convert(isbn):
                    self._add(sameas, "http://data.kbresearch.nl/isbn:"+isbn, "same")
        else:
            url = self.URL_SAMEASQ % sameas
            data = self.get(url)
            if type(data) == list:
                for item in data[0]["duplicates"]:
                    if item.find('http://rdf.freebase.com/ns/') > -1:
                        item=item.replace('http://rdf.freebase.com/ns/', 'http://data.kbresearch.nl/fb:/').replace('en.','en/').replace('guid.','guid/')
                    self._add(sameas, item.replace('http://dbpedia.org/resource/','http://data.kbresearch.nl/DBP:'), "same")
def _usage(stream):
    stream.write(SameAs.__doc__ + "\n")

def main(arguments):
    from pprint import pprint
    import getopt
    try:
        opts, args = getopt.getopt(arguments, program_name+":", ["help", "version", "license"])
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
        sameas = sameAs(args,log_path="./", debug=True)
        sameas.execute()
        pprint(sameas)
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
