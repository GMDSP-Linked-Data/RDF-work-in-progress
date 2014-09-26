#!/usr/bin/env python
"""

film.py: a simple tool to manage your movies review
Simon Rozet, http://atonie.org/

@@ :
- manage directors and writers
- manage actors
- handle non IMDB uri
- markdown support in comment

Requires download and import of Python imdb library from
http://imdbpy.sourceforge.net/ - (warning: installation
will trigger automatic installation of several other packages)

--
Usage:
    film.py whoami "John Doe <john@doe.org>"
        Initialize the store and set your name and email.
    film.py whoami
        Tell you who you are
    film.py http://www.imdb.com/title/tt0105236/
        Review the movie "Reservoir Dogs"
"""
import datetime, os, sys, re, time
from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE
import xml.etree.ElementTree as ET

from tempfile import mktemp
try:
    import imdb
except ImportError:
    imdb = None

from rdflib import BNode, Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import FOAF, DC

import csv
import pprint

storefn = os.path.dirname(os.path.realpath(__file__)) + '/output/streetlight-stockport.rdf'
#storefn = '/home/simon/codes/film.dev/movies.n3'
storeuri = 'file://'+storefn
title = 'Movies viewed by %s'

r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
SPACIAL = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
SCHEMA = Namespace('http://schema.org/')
sl = Namespace('http://data.gmdsp.org.uk/id/stockport/street-lights/')
streetdef = Namespace('http://data.gmdsp.org.uk/def/council/streetlighting/')

class Store:
    def __init__(self):

        self.graph = Graph(identifier=URIRef('http://www.google.com'))

        rt = self.graph.open(storeuri, create=False)
        if rt == None:
            # There is no underlying Sleepycat infrastructure, create it
            self.graph.open(storeuri, create=True)
        else:
            assert rt == VALID_STORE, 'The underlying store is corrupt'

        self.graph.bind('os', OS)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('geo', GEO)
        self.graph.bind('schema', SCHEMA)
        self.graph.bind('spacial', SPACIAL)
        self.graph.bind('streetlamp', streetdef)

    def save(self):
        print storeuri
        self.graph.serialize(storeuri, format='pretty-xml')

    def new_streetlight(self, height, easting, northing, street, objectId, lamptype, watt):
        streetlamp = sl[objectId]
        self.graph.add((streetlamp, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/streetlighting/Streetlight')))
        self.graph.add((streetlamp, RDFS['label'], Literal(objectId)))
        if height != 0:
            self.graph.add((streetlamp, streetdef['columnHeight'], Literal(height)))
        self.graph.add((streetlamp, SPACIAL['easting'], Literal(easting)))
        self.graph.add((streetlamp, SPACIAL['northing'], Literal(northing)))
        self.graph.add((streetlamp, streetdef['lampType'], Literal(lamptype)))
        if watt != 0:
            self.graph.add((streetlamp, streetdef['wattage'], Literal(watt)))
        self.graph.add((streetlamp, VCARD["hasAddress"], Literal(self.new_address(easting, northing, street))))

    def new_address(self, easting, northing, street):
        vcard = sl["address/"+street.replace(" ", "-").replace(",", "")]
        self.graph.add((vcard, RDF.type, VCARD["Location"]))
        self.graph.add((vcard, RDFS['label'], Literal(street)))
        self.graph.add((vcard, VCARD['street-address'], Literal(street)))
        return vcard

def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()

    tree = ET.parse('./Data/streetlighting.xml')
    root = tree.getroot()
    for child in root:
        #for each street light
        for c in child:
            #for each atribute in street light
            try:
                print " -------- "
                print c[0].text
                print c[1].text
                print c[2].text
                print c[3].text
                print c[4].text
                print c[5].text
                print c[6].text
                print c[7].text
                print c[8].text
                print c[9].text
                print c[10].text
                s.new_streetlight(0, c[8].text, c[9].text, c[3].text, c[0].text, c[1].text, 0)
            except:
                print "Unexpected error:", sys.exc_info()[0]
    s.save()

if __name__ == '__main__':
    main()