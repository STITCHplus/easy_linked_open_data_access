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
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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

from backend import Backend

__all__ = ["DBPedia"]

__author__ =    "Willem Jan Faber <wjf@fe2.nl>"
__version__ =   "1.0"
__date__ =      "2011-11-15"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__ =   "GNU GPL"

program_name = sys.argv[0] if len(sys.argv[0]) > 0 else "dbpedia"

class DBPedia(Backend):
    '''Dbpedia a easy to use library to get a dbpedia record, cache and parse it.
Usage: dbpedia.py <dbpedia_identifier> 
    ''' 
    #% globals()

    DBPEDIA_URL = "http://dbpedia.org/data/%s.jsond"

    namespaces = {  'http://www.w3.org/2003/01/geo/wgs84_pos#' : 'pos', 
                    'http://dbpedia.org/property/': 'dbpediaprop',
                    'http://purl.org/dc/elements/1.1/' : 'dc',
                    'http://purl.org/dc/terms/' : 'dcterms',
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'w3',
                    'http://xmlns.com/foaf/0.1/' : 'foaf',
                    'http://dbpedia.org/ontology/' : 'dbpediaont',
                    'http://www.w3.org/2002/07/owl#' : 'owl',
                    'http://www.w3.org/2000/01/rdf-schema#' : 'rdf' }

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
            self.setup_logfile("dbpedia", args["log_path"])

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
        for dbpedia_identifier in self.request:
            if not dbpedia_identifier.find(':') > -1:
                self._get_dbpedia_record(urllib.quote(dbpedia_identifier.encode('utf-8')))
            else:
                identifier = dbpedia_identifier.split(':')[0]+":"+urllib.quote(dbpedia_identifier.split(':')[-1])
                self._get_dbpedia_record(identifier)

    def set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)


    def _get_dbpedia_record(self, dbpedia_identifier):
        if self.debug:
            self.log.info("getting.. %s " % (dbpedia_identifier))
        if dbpedia_identifier.lower().find("http") > -1:
            if dbpedia_identifier.find('http:/') > -1:
                dbpedia_identifier = dbpedia_identifier.split('/')[-1].strip()
            elif dbpedia_identifier.find('%2F') > -1:
                dbpedia_identifier = dbpedia_identifier.split('%2F')[-1].strip()
        if dbpedia_identifier.lower().startswith("dbp:") or dbpedia_identifier.lower().startswith("dbpedia:"):
            dbpedia_identifier = dbpedia_identifier.split(':')[0]

        if dbpedia_identifier[0].islower():
            dbpedia_identifier = dbpedia_identifier.title()
        if dbpedia_identifier.find(' ') > -1:
            dbpedia_identifier = dbpedia_identifier.replace(" ","_")

        url = self.DBPEDIA_URL % dbpedia_identifier.strip()
        data = self.get(url)

        if not data:
            if self.debug:
                self.log.info("No DBPedia data for: %s @ %s (via %s)" % (dbpedia_identifier, url, self.backend))
        else:
            retval = self._parse_dbpedia_response(url, data, dbpedia_identifier)
            if type(retval) == unicode:
                url = self.DBPEDIA_URL % retval.split('/')[-1]
                data = self.get(url)
                self._parse_dbpedia_response(url, data, retval.split('/')[-1])

    def _parse_dbpedia_response(self, url, data, dbpedia_identifier):
        if self.debug:
            self.log.info("Parsing dbpedia response for %s (%s)" % (dbpedia_identifier, url))
        if type(data) == bool:
            return(False)

        resource = ".".join(url.replace('/data/', '/resource/').split('.')[:-1])

        if resource in data:
            if "http://dbpedia.org/ontology/wikiPageRedirects" in data[resource]:
                nurl = data[resource]["http://dbpedia.org/ontology/wikiPageRedirects"][0]["value"]
                if self.debug:
                    self.log.info("Got redirected from %s to %s while parsing record" % (url, nurl)) 
                return(nurl)

        for item in data:
            if resource == item:
                for i in data[item]:
                    if len(data[item][i]) == 1:
                        d=data[item][i][0]
                        if "lang" in d:
                            self._add(dbpedia_identifier, d["value"], i.split('/')[-1]+"_"+d["lang"])
                        else:
                            self._add(dbpedia_identifier, d["value"], i.split('/')[-1].split('#')[-1])

                    else:
                        for name in data[item][i]:
                            if "lang" in name:
                                self._add(dbpedia_identifier, name["value"], i.split('/')[-1].split('#')[-1]+"_"+name["lang"])
                            else:
                                self._add(dbpedia_identifier, name["value"], i.split('/')[-1].split('#')[-1])
            else:
                for name in data[item]:
                    if u'value' in data[item][name][0]:
                        self._add(dbpedia_identifier, data[item][name][0][u'value'], name.split('/')[-1].split('#')[-1])
                    #print(data[item][name])

        return(True)

def _usage(stream):
    stream.write(DBPedia.__doc__ + "\n")

def main(arguments):
    from pprint import pprint
    import getopt
    try:
        opts, args = getopt.getopt(arguments, "dbpedia:", ["help", "version", "license"])
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
        dbp = DBPedia(args)
        dbp.execute()
        pprint(dbp)
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
