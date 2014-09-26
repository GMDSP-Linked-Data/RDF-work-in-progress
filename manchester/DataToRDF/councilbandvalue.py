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
import utm
from bs4 import BeautifulSoup

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/counciltaxband.rdf'
#storefn = '/home/simon/codes/film.dev/movies.n3'
storeuri = 'file://'+storefn
title = 'Movies viewed by %s'

r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
al = Namespace('http://data.gmdsp.org.uk/id/manchester/counciltaxbands/')
SCHEME = Namespace('http://schema.org/')

class Store:
    def __init__(self):
        self.graph = Graph()

        rt = self.graph.open(storeuri, create=False)
        if rt == None:
            # There is no underlying Sleepycat infrastructure, create it
            self.graph.open(storeuri, create=True)
        else:
            assert rt == VALID_STORE, 'The underlying store is corrupt'

        self.graph.bind('os', OS)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('geo', GEO)
        self.graph.bind('vcard', VCARD)
        self.graph.bind('scheme', SCHEME)

    def save(self):
        self.graph.serialize(storeuri, format='pretty-xml')

    def new_bandvalue(self, band, charge):
        allotment = al[band] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/counciltax/CouncilTaxCharge')))
        self.graph.add((allotment, URIRef('http://data.gmdsp.org.uk/def/council/counciltax/charge'), Literal(charge)))
        self.graph.add((allotment, URIRef('http://data.gmdsp.org.uk/def/council/counciltax/councilTaxBand'), URIRef('http://data.gmdsp.org.uk/def/council/counciltax/council-tax-bands/'+band)))
        self.graph.add((allotment, RDFS.label, Literal('Council tax valuation charges for band '+band, lang='en')))
        self.save()

def help():
    print(__doc__.split('--')[1])

def getURL(html):
    soup = BeautifulSoup(html)
    links = soup.find_all('a')

    for tag in links:
        link = tag.get('href',None)
        if link != None:
            return link[1:-2]
    return ""

def main(argv=None):
    s = Store()

    reader = csv.DictReader(open('./Data/councilBandValue.csv', mode='rU'))
    for row in reader:
        s.new_bandvalue(row["Band"], row["Charge"])
        pprint.pprint(row)

if __name__ == '__main__':
    main()