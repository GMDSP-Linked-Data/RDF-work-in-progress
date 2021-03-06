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

from tempfile import mktemp
try:
    import imdb
except ImportError:
    imdb = None

from rdflib import BNode, Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import FOAF, DC

import csv
import pprint

storefn = os.path.dirname(os.path.realpath(__file__)) + '/output/streetlight.rdf'
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
sl = Namespace('http://data.gmdsp.org.uk/id/manchester/street-lights/')
streetdef = Namespace('http://data.gmdsp.org.uk/def/council/streetlighting/Streetlight')

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
        self.graph.serialize(storeuri, format='pretty-xml')

    #def new_streetlight(self, height, easting, eligible, lamp, lampwatts, location, mintyn, northing, objectId, street, unitid, unitno):
    def new_streetlight(self, height, easting, northing, street, objectId, lamptype, watt):
        streetlamp = sl[objectId] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((streetlamp, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/streetlighting/Streetlight')))
       # self.graph.add((streetlamp, streetdef['columnHeight'], Literal(height)))
        self.graph.add((streetlamp, SPACIAL['easting'], Literal(easting)))
        self.graph.add((streetlamp, SPACIAL['northing'], Literal(northing)))
        self.graph.add((streetlamp, VCARD['street-address'], Literal(street)))
        self.graph.add((streetlamp, streetdef['lampType'], Literal(lamptype)))
        self.graph.add((streetlamp, streetdef['wattage'], Literal(watt)))
        #self.graph.add((allotment, GEO["lat//long"], Literal(location)))
        #self.graph.add((allotment, RDFS['label'], Literal(name)))
        #self.graph.add((allotment, DC['date'], Literal(plot_size)))
        #self.graph.add((allotment, GEO['rating'], Literal(rent)))


def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()

    reader = csv.DictReader(open('./Data/Street_Lighting.txt',"rU"))

    first = True
    for row in reader:
        if first == True:
            print "Skipping first row."
            first = False
        else:
            s.new_streetlight(0,row["Easting"], row["Northing"], row['Address 1'], row["Unit No."]+""+row['Address 1'], row["LT - LAMP TYPE"], row["LW - LAMP WATTS"])
    s.save()

if __name__ == '__main__':
    main()