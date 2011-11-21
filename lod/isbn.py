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
import feedparser

try:
    import json
except:
    import simplejson as json

try:
    import warnings
    warnings.filterwarnings("ignore")
except:
    pass

import lxml_lib
from backend import Backend
sys.path.append(os.path.dirname(__file__))
import isbn_check 

__all__         = ["Isbn"]
__author__      = "Willem Jan Faber <willemjan@fe2.nl>"
__version__     = "1.0"
__date__        = "2011-11-15"
__copyright__   = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__
__licence__     = "GNU GPL"

program_name = sys.argv[0] if len(sys.argv[0]) > 0 else "isbn"

class Isbn(Backend):
    '''Isbn a easy to use library to find information about an ISBN number, cache and parse it.
Usage: isbn <ISBN> 
    ''' 

    sru_crap = "&version=1.1&operation=searchRetrieve&maximumRecords=1"
    SRU_SERVERS = { "http://jsru.kb.nl/sru?query=%s"+sru_crap+"&recordSchema=%s&x-collection=GGC": True,
                    "http://z3950.loc.gov:7090/voyager?query=%s"+sru_crap+"&recordSchema=%s": True }

    WORLDCAT_KEY = "YOUR_KEY_HERE"
    URL_WORLDCAT = "http://www.worldcat.org/webservices/catalog/search/opensearch?q=%s&wskey=%s"

    ISBNDB_KEY = "YOUR KEY HERE"
    URL_ISBNDB = "http://isbndb.com/api/books.xml?access_key=%s&index1=isbn&value1=%s"

    URL_OPENLIBRARY = "http://openlibrary.org/api/books?bibkeys=ISBN:%s&callback=mycallback&jscmd=data"

    URL_RYERSON = "http://news.library.ryerson.ca/api/isbnsearch.php?isbn=%s"

    URL_GOOGLE = "http://books.google.com/books/feeds/volumes?q=%s"

    URL_THING = "http://www.librarything.com/api/thingISBN/%s"

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
            self.setup_logfile("isbn", args["log_path"])

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
        for isbn in self.request:
            self._get_isbn_record(isbn)

    def _set_backend(self, backend):
        if not backend in self.backends:
            self.backend = self.default_backend
        else:
            self.backend = backend
        if self.debug:
            self.log.info("Setting backend to: %s.", self.backend)
        return(True)

    def _get_isbn_record(self, isbn):
        if isbn_check.isValid(isbn):
            self.isbn=isbn
            self._sameas()
            self._sru_lookup()
            self._openlibrary_lookup()
            self._ryerson_lookup()
            self._google_lookup()

            for item in self.keys():
                if len(self[item]) == 0:
                    self.__delitem__(item)

            self.isbn=isbn_check.convert(isbn)
            if not "ryerson" in self.keys():
                self._ryerson_lookup()
            if not "openlibrary" in self.keys():
                self._openlibrary_lookup()
            if not "google" in self.keys():
                self._google_lookup()
            if not "librarything_sameas" in self.keys():
                self._sameas()
            if not "sru" in self.keys():
                self._sru_lookup()

            for item in self.keys():
                if len(self[item]) == 0:
                    self.__delitem__(item)

    def _sameas(self):
        data = self.get(self.URL_THING % self.isbn)
        xml = lxml_lib.fromstring(data)
        for item in xml.iterchildren():
            isbn = str(item.text)
            if not self.isbn == isbn and not self.isbn == isbn_check.convert(isbn):
                self._add("librarything_sameas", "http://data.kbresearch.nl/isbn:"+isbn, "isbn")

    def _sru_lookup(self):
        for server in self.SRU_SERVERS.keys():
            if not server.find('GGC') > -1:
                schema = 'mods'
            else:
                schema = 'dcx'
            url=server% (self.isbn, schema)
            data=self.get(url)
            if data == False: return(False)
            data=lxml_lib.fromstring(data)
            found = int(data.find("{http://www.loc.gov/zing/srw/}numberOfRecords").text)
            if found>0:
                data=data.find("{http://www.loc.gov/zing/srw/}records").find("{http://www.loc.gov/zing/srw/}record").find("{http://www.loc.gov/zing/srw/}recordData")
                if schema =='dcx': 
                    data = data.find("{info:srw/schema/1/dc-v1.1}dc")
                else:
                    data = data.find("{http://www.loc.gov/mods/v3}mods")
                for item in data.getchildren():
                    if len(item.getchildren()) > 0:
                        for name in item.getchildren():
                            if len(name.text.strip()) > 0:
                                nname=nname=item.tag.split('}')[1]+"_"+name.tag.split('}')[1]
                                self._add("sru", name.text, nname)
                    if len(item.text.strip())>0:
                        self._add("sru", item.text, item.tag.split('}')[1])

    def _google_lookup(self):
        url = self.URL_GOOGLE % self.isbn
        data=self.get(url)
        result = feedparser.parse(data)
        self["google"] = {}
        if "opensearch_totalresults" in result["feed"]:
            if int(result["feed"]["opensearch_totalresults"]) > 0:
                for item in result["entries"]:
                    for name in item.keys():
                        try:
                            self["google"][name]=str(item[name])
                        except:
                            pass
                    
    def _worldcat_lookup(self):
        url = self.worldcat %(self.isbn, self.worldcat_key)
        data=url_cache.getURLdata(url)
        data=lxml_lib.fromstring(data)
        self.data["worldcat"] = {}
        if int(data.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text) > 0:
            for item in data.find('{http://www.w3.org/2005/Atom}entry').getchildren():
                if item.text:
                    if len(item.text.strip()) > 0:
                        if not item.tag.split('}')[1] in self.data["worldcat"].keys():
                            self.data["worldcat"][item.tag.split('}')[1]] = {}
                        self.data["worldcat"][item.tag.split('}')[1]][item.text] = True
                if len(item.getchildren()) > 0:
                    for name in item.getchildren():
                        if name.text:
                            if len(name.text.strip()) > 0:
                                nname = item.tag.split('}')[1]+"_"+name.tag.split('}')[1]
                                if not nname in self.data["worldcat"].keys():
                                    self.data["worldcat"][nname] = {}
                                self.data["worldcat"][nname][name.text] = True
                                #self._add(dbpedia_identifier, val, nns)
                   
    def _isbndb_lookup(self):
        data = url_cache.getURLdata(url)
        data = lxml_lib.fromstring(data)
        self.data["isbndb"] = {}
        try:
            if data.find('BookList').find('BookData'):
                for item in data.find('BookList').find('BookData').getchildren():
                    if not item.tag in self.data["isbndb"].keys():
                        self.data["isbndb"][item.tag]={}
                    self.data["isbndb"][item.tag][item.text] = True
                    #self._add(dbpedia_identifier, val, nns)
        except:
            pass
        
    def _openlibrary_lookup(self):
        data=self.get(self.URL_OPENLIBRARY % self.isbn, mode="raw")
        data=json.loads(data.replace('mycallback(','')[:-2])
        self["openlibrary"] = data

    def _ryerson_lookup(self):
        data=self.get(self.URL_RYERSON % self.isbn)
        if type(data) == bool: return(False)
        self["ryerson"] = {}
        data=lxml_lib.fromstring(data)
        for item in data.findall('record'):
            for name in item.getchildren():
                if name.text:
                    if len(name.text.strip()) > 0:
                        self._add("ryerson",name.text.replace('&zoom=5', '&zoom=1'), name.tag.replace('_url', ''))



def _usage(stream):
    stream.write(Isbn.__doc__ + "\n")

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
        isbn = Isbn(args,log_path="./", debug=True)
        isbn.execute()
    else:
        sys.stdout.write("Did not get any arguments.")
        _usage(sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
