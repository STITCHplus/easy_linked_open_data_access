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

import zlib
import hashlib
import string
import urllib2

try:
    import json
except:
    import simplejson as json

try:
    import socket
    socket.setdefaulttimeout(49300)
except:
    pass

from pprint import pprint

__all__ = ["Backend"]
__author__ =    "Willem Jan Faber <willemjan@fe2.nl>"
__version__ =   "1.0"
__licence__ =   "GNU GPL"
__copyright__ = "Copyright (c) 2011 National library of the Netherlands, %s. All rights reserved." % __author__


class Backend(dict):
    """ test """
    default_backend = "nocache"

    backends = {"pymongo"  :  {}, "tmpfiles" :  {}, "nocache"  :  {} }

    pymongo= {"conn" : None,
              "host" : None,
              "port" : None,
              "database" : "backend",
              "collection" : "cache",
              "broken": False}

    couchdb = pymongo
    http_retries = 100

    def __init__(self, *fargs, **args):
        for item in self.backends.keys():
            self.backends[item]["get"] = getattr(self, "_get_" + item)

    def _get_nocache(self, url, mode=""):
        if self.debug:
            self.log.debug("Getting %s (via %s)" % (url, self.backend))
        headers = {'Accept' : '*/*'}
        req = urllib2.Request(url=url, headers = headers)
        try:
            response = urllib2.urlopen(req, timeout=1000 )
        except:
            self.http_retries-=1
            if self.debug:
                self.log.info("Got an http error, sleeping for 10seconds, %s retries to go." % (self.http_retries))
            if self.http_retries > 0:
                time.sleep(10)
                return(self._get_nocache(url, mode))
            else:
                sys.stderr.write("Too manny http errors, giving up.")
                #sys.exit(-1)
                return(False)

        if response.getcode() == 200:
            header = response.info().dict
            if "content-length" in header:
                if string.atoi(header["content-length"]) > 10:
                    if self.debug:
                        self.log.debug("Got %s bytes for %s (via %s)" % (url, response.info().dict["content-length"], self.backend))
                    data=response.read()
                else:
                    if self.debug:
                        self.log.debug("Content of  %s is smaller than 10bytes (via %s)" % (url, self.backend))
                    return(False)
                if "content-type" in header:
                    if header["content-type"].lower().find('json') > -1 and not mode=="raw":
                        if self.debug:
                            self.log.debug("Content type json detected converting %s bytes into json" % (len(data)) )
                        return(json.loads(data))
                    else:
                        return(data)
                else:
                    self.log.debug("No content type in header..")
                    return(data)
            else:
                try:
                    data=response.read()
                    return(data)
                except:
                    self.log.debug("Abort get")

                    return(False)
        self.log.debug("Abort get")
        return(False)
                
    def _get_tmpfiles(self, url, mode):
        pass

    def _get_pymongo(self, url, mode):
        if self.pymongo["broken"]:
            return(self._get_nocache(url, mode))

        if not hasattr(self, "mongo"):
            self.mongo = __import__(self.backend)
            self.binary = __import__(self.backend+".binary")
            try:
                self.mongo = __import__(self.backend)
                self.binary.Binary = self.mongo.binary.Binary
            except:
                self.pymongo["broken"]=True
                if self.debug:
                    self.log.info("Could not import pymongo module.")
                    return(False)

        if self.pymongo["conn"] == None:
            try:
                self.pymongo["conn"] = self.mongo.Connection(host=self.pymongo["host"], port=self.pymongo["port"])
                if self.debug:
                    host="localhost" if self.pymongo["host"] == None else self.pymongo["host"]
                    path=host if self.pymongo["port"] == None else host+":"+self.pymongo["port"]
                    if self.debug:
                        self.log.info("Successfully made connection to mongodb @ %s." % path)
            except:
                self.pymongo["broken"] = True
                if self.debug:
                    host="localhost" if self.pymongo["host"] == None else self.pymongo["host"]
                    port="" if self.pymongo["port"] == None else self.pymongo["port"]
                    if self.debug:
                        self.log.info("Could not create a MongoDB connction with: %s:%s" % (host, port))
                return(False)

        myhash = hashlib.md5(url).hexdigest()
        self.log.debug("Getting %s (via %s)" % (url, self.backend))

        if self.pymongo["database"] in self.pymongo["conn"].database_names():
            if self.pymongo["collection"] in self.pymongo["conn"][self.pymongo["database"]].collection_names():
                conn = self.pymongo["conn"][self.pymongo["database"]][self.pymongo["collection"]]
                data = conn.find_one({"id" : myhash})
                if (data == None):
                    self.log.debug("No data in mongodb for %s, procedeeding to fetch data." % url)
                    conn = self.pymongo["conn"][self.pymongo["database"]][self.pymongo["collection"]]
                    data = self._get_nocache(url, "raw")
                    if type(data) == bool:
                        conn.insert({"id" : myhash, "data" : False})
                        return(False)
                    sdata = self.binary.Binary(zlib.compress(data))
                    if self.debug:
                        self.log.info("Stored %s bytes for %s (%s)" % (len(sdata), url, myhash))
                    conn.insert({"id" : myhash, "data" : sdata})
                    try:
                        data = json.loads(data)
                    except:
                        return(data)
                    return(data)
                else:
                    if type(data["data"]) == bool:
                        return(data["data"])
                    if self.debug:
                        self.log.info("Got %s bytes for %s (%s)." % (len(data["data"]), url, myhash))
                    data = zlib.decompress(data["data"])
                    if self.debug:
                        self.log.info("Decompressed to %s bytes (%s)." % (len(data), myhash))
                    try:
                        data = json.loads(data)
                        if self.debug:
                            self.log.info("Loaded %s: (%s) from pymongo." % (url, myhash))
                    except:
                        if self.debug:
                            self.log.info("Failed to parse data to json for: %s (%s)." % (url, myhash))
                            return(data)
                        data = False
                    return(data)
        else:
            if self.debug:
                self.log.info("Creating new database/collection: %s/%s" % (self.pymongo["database"], self.pymongo["collection"]))
            conn = self.pymongo["conn"][self.pymongo["database"]][self.pymongo["collection"]]
            data = self._get_nocache(url, "raw")
            sdata = self.binary.Binary(zlib.compress(data))
            if self.debug:
                self.log.info("Storing %s bytes for %s (%s)" % (len(sdata), url, myhash))
            conn.insert({"id" : myhash, "data" : sdata})
            try:
                data = json.loads(data)
            except:
                if self.debug:
                    self.log.info("Failed to parse data to json for: %s (%s)." % (url, myhash))
                data = False
            return(data)

    def setup_logfile(self, log_name, log_path="/tmp"):
        import logging
        logging.basicConfig(filename=log_path+os.sep+log_name+".log",level=logging.DEBUG)
        self.log = logging.getLogger(log_name)

    def get(self, url, mode="parse"):
        data = self.backends[self.backend]["get"](url, mode)
        return(data)

    def _add(self, identifier, value, namespace):
        if not identifier in self.keys():
            self[identifier]={}

        if not namespace in self[identifier].keys():
            self[identifier][namespace] = ""
        else:
            if not type(self[identifier][namespace]) == list:
                val = self[identifier][namespace]
                if not value == val:
                    self[identifier][namespace]=[val]
        if (type(value) == unicode) or (type(value) == str):
            value = value.replace('http://dbpedia.org/resource/', 'http://data.kbresearch.nl/DBP:').replace('http://dbpedia.org/ontology/', 'http://data.kbresearch.nl/DBP:')
            value = value.replace('http://rdf.freebase.com/ns/', 'http://data.kbresearch.nl/FB:').replace('http://www.freebase.com/view/', 'http://data.kbresearch.nl/FB:')


            if value.isdigit():
                if type(self[identifier][namespace]) == list:
                    if not value in self[identifier][namespace]:
                        try:
                            self[identifier][namespace].append(int(value))
                        except:
                            self[identifier][namespace].append(value)
                else:
                    try:
                        self[identifier][namespace] = int(value)
                    except:
                        self[identifier][namespace] = value
            else:
                if type(self[identifier][namespace]) == list:
                    if not value in self[identifier][namespace]:
                        self[identifier][namespace].append(value)
                else:
                    self[identifier][namespace]=value
        else:
            if type(self[identifier][namespace]) == list:
                if not value in self[identifier][namespace]:
                    self[identifier][namespace].append(value)
            else:
                self[identifier][namespace]=value
