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
from dbpedia import DBPedia
from sameas import sameAs

__all__ = ["DBPedia_nl"]

__author__ =    "Willem Jan Faber <willemjan@fe2.nl>"
__version__ =   "1.0"
__licence__ =   "GNU GPL"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__

program_name = sys.argv[0] if len(sys.argv[0]) > 0 else "dbpedia_nl"

class DBPedia_nl(Backend):
    '''Dbpedia a easy to use library to get a dbpedia_nl record, cache and parse it.
Usage: dbpedia_nl.py <dbpedia_nl_identifier> 
    ''' 
    #% globals()

    DBPEDIA_NL_URL = "http://tomcat.kbresearch.nl/solr/dbpedia/select/?q=(prefLabel:\"%s\"%s)+AND+NOT+disambiguation&wt=json&rows=1&fl=id"

    def __init__(self, *fargs, **args):
        Backend.__init__(self, *fargs, **args)
        self.log_path = None
        if "log_path" in args:
            self.log_path=args["log_path"]
            if "debug" in args:
                self.debug = args["debug"]
            else:
                self.debug = True
        else:
            self.debug = False

        if self.debug:
            self.setup_logfile("dbpedia_nl", args["log_path"])

        if "backend" in args:
            self.set_backend(args["backend"])
            self.backend=args["backend"]
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
        for dbpedia_nl_identifier in self.request:
            self._get_dbpedia_nl_record(dbpedia_nl_identifier)

    def set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)


    def _get_dbpedia_nl_record(self, dbpedia_nl_identifier):
        if self.debug:
            self.log.info("getting.. %s " % (dbpedia_nl_identifier))
        if dbpedia_nl_identifier.lower().find("http") > -1:
            if dbpedia_nl_identifier.find('http:/') > -1:
                dbpedia_nl_identifier = dbpedia_nl_identifier.split('/')[-1].strip()
            elif dbpedia_nl_identifier.find('%2F') > -1:
                dbpedia_nl_identifier = dbpedia_nl_identifier.split('%2F')[-1].strip()
        if dbpedia_nl_identifier.lower().startswith("dbp:") or dbpedia_nl_identifier.lower().startswith("dbpedia_nl:"):
            dbpedia_nl_identifier = dbpedia_nl_identifier.split(':')[0]

        if dbpedia_nl_identifier[0].islower():
            dbpedia_nl_identifier = dbpedia_nl_identifier.title()
        if dbpedia_nl_identifier.find(' ') > -1:
            dbpedia_nl_identifier = dbpedia_nl_identifier.replace(" ","_")
        if dbpedia_nl_identifier.find('%20') > -1:
            dbpedia_nl_identifier = dbpedia_nl_identifier.replace("%20","_")

        if dbpedia_nl_identifier.find('+') > -1 or dbpedia_nl_identifier.find('_') > -1:
            q=""
            for item in dbpedia_nl_identifier.split('+'):
                q+="+OR+prefLabel:"+item
            for item in dbpedia_nl_identifier.split('_'):
                q+="+OR+prefLabel:"+item
            url = self.DBPEDIA_NL_URL % (dbpedia_nl_identifier.strip() ,q)
        else:
            url = self.DBPEDIA_NL_URL % (dbpedia_nl_identifier.strip(), "+OR+"+dbpedia_nl_identifier.strip())
        data = self.get(url)

        if not data:
            if self.debug:
                self.log.info("No DBPedia_nl data for: %s @ %s (via %s)" % (dbpedia_nl_identifier, url, self.backend))
            return(False)
        else:
            if type(data) == str:
                data=json.loads(data)            
            if data["response"]["numFound"] > 0:
                identifier = data["response"]["docs"][0]["id"].split('/')[-1]
                record = DBPedia([identifier], backend=self.backend, log_path=self.log_path, debug=self.debug)
                record.execute()
                self[record.keys()[0]] = record[record.keys()[0]]
                s=self[record.keys()[0]].pop("sameAs")[0]
                rec = sameAs([s], backend=self.backend, log_path=self.log_path, debug=self.debug)
                rec.execute()
                self[record.keys()[0]]["same"] = rec.values()[0]["same"]
                

def _usage(stream):
    stream.write(DBPedia_nl.__doc__ + "\n")

def main(arguments):
    from pprint import pprint
    import getopt
    try:
        opts, args = getopt.getopt(arguments, "dbpedia_nl:", ["help", "version", "license"])
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
        dbp = DBPedia_nl(args)
        dbp.execute()
        pprint(dbp)
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
