#!/usr/bin/python

##
## lod.py - easy_linked_open_data_access
##
## copyright (c) 2011-2012 Koninklijke Bibliotheek - National library of the Netherlands.
##
## this program is free software: you can redistribute it and/or modify
## it under the terms of the gnu general public license as published by
## the free software foundation, either version 3 of the license, or
## (at your option) any later version.
##
## this program is distributed in the hope that it will be useful,
## but without any warranty; without even the implied warranty of
## merchantability or fitness for a particular purpose. see the
## gnu general public license for more details.
##
## you should have received a copy of the gnu general public license
## along with this program. if not, see <http://www.gnu.org/licenses/>.
##

__author__ = "Willem Jan Faber"
__licence__ = "GNU GPL"

import urllib2
import json
import sys
import os

from wsgiref.handlers import CGIHandler
from flask import Flask
from flask import request, abort, redirect, url_for, jsonify, escape
from pprint import pprint

sys.path.append(os.path.dirname(__file__))

application = Flask("dbpedia")
application.debug = False

PYMONGO_HOST = "127.0.0.1"
BASEURL="http://data.kbresearch.nl/"

@application.route('/')

@application.route('/trove:<path:identifier>')
@application.route('/TROVE:<path:identifier>')

@application.route('/isbn:<path:identifier>')
@application.route('/ISBN:<path:identifier>')

@application.route('/geo:<path:identifier>')
@application.route('/GEO:<path:identifier>')

@application.route('/dbp_nl:<path:identifier>')
@application.route('/DBP_nl:<path:identifier>')


@application.route('/dbp:<path:identifier>')
@application.route('/DBP:<path:identifier>')

@application.route('/fb:/<path:identifier>')
@application.route('/fb:<path:identifier>')
@application.route('/FB:/<path:identifier>')
@application.route('/FB:<path:identifier>')


@application.route('/SameAs:<path:identifier>')
@application.route('/sameAs:<path:identifier>')
@application.route('/sameas:<path:identifier>')


def lod(identifier = None):
    global BASEURL
    index = """<html>
        <head>
          <style type="text/css">
            div { background-color: #b8babd;
                  margin-top: 30px;
                  width: 1100px; 
                  height: 500px; 
                  margin-left: auto; 
                  margin-right: auto;
                  border-style: solid;
                  border-width: 1px;}
            a { color: red; text-decoration: none; }
            a:link { color: red; text-decoration: none; }
            a:visited { color: red; text-decoration: none; }
            a:hover { text-decoration: underline; }
            iframe { border-style: solid;
                    border-width: 1px;
                    margin: 5px;
            }
        </style>

        </head>

        <body>

        <div id="dbp">
        <iframe src="%(baseurl)s/DBP:Albert_Einstein?label_nl,thumbnail,comment_nl&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align:left'><b>DBP:</b> DBPedia</h4>
        <a href="%(baseurl)s/DBP:Albert_Einstein">%(baseurl)s/DBP:Albert_Einstein</a><br>
        <a href="%(baseurl)s/DBP:Albert_Einstein?label_nl">%(baseurl)s/DBP:Albert_Einstein?label_nl</a><br>
        <a href="%(baseurl)s/DBP:Albert_Einstein?label_nl,depiction,deathYear,birthYear,viaf">%(baseurl)s/DBP:Albert_Einstein?label_nl,depiction,deathYear,viaf</a><br>
        <a href="%(baseurl)s/DBP:Albert_Einstein?depiction&callback=dbpedia">%(baseurl)s/DBP:Albert_Einstein?depiction&callback=dbpedia</a><br>
        <a href="%(baseurl)s/DBP:Albert_Einstein?depiction&mode=html">%(baseurl)s/DBP:Albert_Einstein?depiction&mode=html</a><br>
        <a href="%(baseurl)s/dbp:http://dbpedia.org/resource/Engelbert_Humperdinck?depiction">%(baseurl)s/dbp:http://dbpedia.org/resource/Engelbert_Humperdinck?depiction</a><br>
        </div>

        <div id="dbpedia_nl">
        <iframe src="%(baseurl)s/DBP_nl:lichtsnelheid?label_nl,thumbnail,comment_nl,abstract_nl&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align: left'><b>DBP_nl:</b> DBPedia_nl (solr)</h4>
        <a href="%(baseurl)s/DBP_nl:lichtsnelheid">%(baseurl)s/DBP_nl:lichtsnelheid</a><br>
        <a href="%(baseurl)s/DBP_nl:lichtsnelheid?label_nl,depiction">%(baseurl)s/DBP_nl:lichtsnelheid?label_nl,depiction,abstract_nl</a><br>
        </div>

        <div id="isbn">
        <iframe src="%(baseurl)s/ISBN:0743264738?title,author,abstract,thumbnail,genre,note&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align: left'><b>ISBN:</b> Isbn</h4>
        <a href="%(baseurl)s/ISBN:0743264738">%(baseurl)s/ISBN:0743264738</a><br>
        <a href="%(baseurl)s/ISBN:0743264738?title">%(baseurl)s/ISBN:0743264738?title</a><br>
        </div>
        
        <div id="freebase">
        <iframe src="%(baseurl)s/FB:en/albert_einstein?thumbnail,description&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align:left'><b>FB:</b> FreeBase</h4>
        <a href="%(baseurl)s/FB:en/albert_einstein">%(baseurl)s/FB:en/albert_einstein</a><br>
        <a href="%(baseurl)s/FB:/en/herman_brood">%(baseurl)s/fb:/en/herman_brood</a><br>
        <a href="%(baseurl)s/FB:/en/herman_brood?description">%(baseurl)s/fb:/en/herman_brood?description</a><br>
        </div>

        <div id="geonames">
        <iframe src="%(baseurl)s/GEO:Ulm?lat,lng,population&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align:left'><b>GEO:</b> Geonames</h4>
        <a href="%(baseurl)s/GEO:Ulm">%(baseurl)s/GEO:Ulm</a><br>
        <a href="%(baseurl)s/GEO:Ulm?lat,lng,population">%(baseurl)s/GEO:Ulm?lat,lng,population</a><br>
        <a href="%(baseurl)s/GEO:Ulm?lat,lng&mode=html">%(baseurl)s/GEO:Ulm?lat,lng&mode=html</a><br>
        </div>

        <div id="sameas">
        <iframe src="%(baseurl)s/SameAs:Albert_Einstein?same&mode=html" width=600 height=490 style='float: right' frameborder='0'></iframe><br>
        <h4 style='text-align:left'><b>SameAs:</b> SameAs</h4>
        <a href="%(baseurl)s/SameAs:http://sws.geonames.org/4994862/">%(baseurl)s/SameAs:http://sws.geonames.org/4994862/</a><br>
        <a href="%(baseurl)s/SameAs:Albert_Einstein">%(baseurl)s/SameAs:Albert_Einstein</a><br>
        <a href="%(baseurl)s/SameAs:0330454358">%(baseurl)s/SameAs:0330454358</a><br>
        <a href="%(baseurl)s/SameAs:http://dbpedia.org/resource/Engelbert_Humperdinck">%(baseurl)s/SameAs:http://dbpedia.org/resource/Engelbert_Humperdinck</a><br>
        </div>

        <div id="trove" style="height: 150px;">
        <iframe src="%(baseurl)s/TROVE:Einstein_Albert?title,link&mode=html" width=600 height=490 style='float: right;height: 140px;' frameborder='0'></iframe><br>
        <h4 style='text-align:left'><b>Trove:</b> Trove</h4>
        <a href="%(baseurl)s/TROVE:Einstein Albert">%(baseurl)s/TROVE:Einstein Albert</a><br>
        </div>

        </body>

    </html>
    """ % ({"baseurl" : BASEURL})
    if not identifier == None:
        request_lod_source = request.path.split(':')[0][1:]

        if not request.args == None:
            req = dict(request.args)
        else:
            req = None

        if "mode" in req:
            if "html" == str(req["mode"][0]):
                mode="html"
                req.__delitem__("mode")
            else:
                mode="json"
                req.__delitem__("mode")
        else:
            mode="json"
    
        callback = False
        if "callback" in req:
            if mode == "json":
                callback = escape(req["callback"][0])
                req.__delitem__("callback")

        if identifier.find('&') > -1:
            if identifier.split('&')[1].split('=')[1].lower().startswith('htm'):
                mode = "html"
            identifier = identifier.split('&')[0]
        elif identifier.startswith('http:/'):
            identifier = identifier.replace('http:/', 'http://')

        if request_lod_source.lower() == "fb":
            from lod.freebase import Freebase

            fb = Freebase([escape("/"+identifier)], log_path='/tmp', debug=True, backend='pymongo')
            fb.pymongo["host"] = PYMONGO_HOST
            fb.execute()

            data=fb
        elif request_lod_source.lower() == "isbn":
            from lod.isbn import Isbn

            isbn = Isbn([escape(identifier)], log_path='/tmp', debug=True, backend='pymongo')
            isbn.pymongo["host"] = PYMONGO_HOST
            isbn.execute()

            data = isbn

        elif request_lod_source.lower() == "dbp":
            from lod.dbpedia import DBPedia

            dbp = DBPedia([escape(identifier)], log_path='/tmp', debug=True, backend='pymongo')
            dbp.pymongo["host"] = PYMONGO_HOST
            dbp.execute()

            data = dbp

        elif request_lod_source.lower() == "dbp_nl":
            from lod.dbpedia_nl import DBPedia_nl

            dbp = DBPedia_nl([escape(identifier)], log_path='/tmp', debug=True, backend='pymongo')
            dbp.pymongo["host"] = PYMONGO_HOST
            dbp.execute()

            data = dbp

        elif request_lod_source.lower() == "geo":
            from lod.geonames import Geonames

            geo = Geonames([urllib2.quote(escape(identifier))], log_path='/tmp', debug=True, backend='pymongo')
            geo.pymongo["host"] = PYMONGO_HOST
            geo.execute()

            data = geo
        elif request_lod_source.lower() == "trove":
            from lod.trove import Trove

            trove = Trove([urllib2.quote(escape(identifier))], log_path='/tmp', debug=True, backend='pymongo')
            trove.pymongo["host"] = PYMONGO_HOST
            trove.execute()

            data = trove
        elif request_lod_source.lower() == "sameas":
            from lod.sameas import sameAs

            sameas = sameAs([urllib2.quote(escape(identifier))], log_path='/tmp', debug=True, backend='pymongo')
            sameas.pymongo["host"] = PYMONGO_HOST
            sameas.execute()

            data = sameas
        else:
            return(lod.__doc__)

        if len(data.keys()) > 0:
            if not req == None:
                if len(req.keys()) > 0:
                    ret = "<div itemscope itemtype=\"%s\">" % escape(identifier)
                    res = {}
                    for space in data.keys():
                        for name in req.keys()[0].split(','):
                            if name in data[space]:
                                if str(mode) == "json":
                                    res[name] = data[space][name]
                                else:
                                    if type(data[space][name]) == unicode or type(data[space][name]) == str:
                                        if data[space][name].lower().find('.jpg') > -1 or \
                                            data[space][name].lower().find('_thumb') > -1 or \
                                            data[space][name].lower().find('img') > -1 or \
                                            data[space][name].lower().find('.svg') > -1 or \
                                            data[space][name].lower().find('.gif') > -1:
                                            if data[space][name].lower().find('_thumb') > -1:
                                                ret += "<img id='"+str(space+"_"+name)+"' src='"+data[space][name]+"'></img><br>"
                                            else:
                                                ret += "<img id='"+str(space+"_"+name)+"' src='"+data[space][name]+"'></img><br>"
                                        elif data[space][name].find('http://') > -1:
                                            ret += "<a id='"+str(space+"_"+name)+"' href='"+data[space][name]+"'>"+data[space][name]+"</a><br>"
                                        else:
                                            ret += "<div id='"+str(space)+"_"+name+"'>"+ name.split('_')[0].title() + ": </div>" + data[space][name]+"</br>"
                                    elif type(data[space][name]) == list:
                                        for item in data[space][name]:
                                            if type(item) == unicode or type(item) == str:
                                                if item.lower().find('.jpg') > -1 or \
                                                    item.lower().find('_thumb') > -1 or \
                                                    item.lower().find('img') > -1 or \
                                                    item.lower().find('.svg') > -1 or \
                                                    item.lower().find('.gif') > -1:
                                                    if item.lower().find('_thumb') > -1:
                                                        ret += "<img id='"+str(space+"_"+name)+"' src='"+item+"'></img><br>"
                                                    else:
                                                        ret += "<img id='"+str(space+"_"+name)+"' src='"+item+"'></img><br>"

                                                elif item.find('http://') > -1:
                                                    ret += "<a id='"+str(space+"_"+name)+"' href='"+item+"'>"+item+"</a><br>"
                                                else:
                                                    ret += "<div id='"+str(space)+"_"+name+"'>"+ name.split('_')[0].title() + ": </div>"+item+"</br>"
                                    else:
                                        if not (name == "lng" or name == "long" or name == "lat"):
                                            ret += "<div id=\"label\">"+name+"<div id='"+str(space)+"_"+name+"'>" +str(data[space][name]) +"</div>"

                    if (req.keys()[0].find('lat') > -1 and req.keys()[0].find('lng') > -1) and mode=="html":
                        lat = str(data[space]['lat'])
                        if "long" in data[space]:
                            lng = str(data[space]['long'])
                        else:
                            lng = str(data[space]['lng'])
                        url = 'http://www.google.com/uds/modules/elements/mapselement/iframe.html?maptype=roadmap&latlng=%s,%s' % (lat, lng)
                        ret+= """<div itemscope itemtype="http://schema.org/Place">\n \
                                <iframe src=%s width=300 height=300></iframe> \n \
                                <div itemprop="geo" itemscope itemtype="http://schema.org/GeoCoordinates"><meta itemprop="latitude" content="%s" />\n \
                                <meta itemprop="longitude" content="%s" />\n""" % (url, lat, lng)

                    if mode == "json":
                        if callback:
                            return(callback+"(["+str(jsonify(res).data) +"]);")
                        else:
                            return(jsonify(res))
                    else:
                        ret+="</div>"
                        return(ret)
                if callback:
                    return(callback + "(["+str(jsonify(data).data) +"]);")
                else:
                    return(jsonify(data))
        return()
    return(index)
