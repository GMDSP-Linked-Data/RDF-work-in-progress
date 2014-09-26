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

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/allotments-tmp.rdf'
#storefn = '/home/simon/codes/film.dev/movies.n3'
storeuri = 'file://'+storefn
title = 'Movies viewed by %s'

r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
al = Namespace('http://data.gmdsp.org.uk/id/manchester/allotments/')
SCHEME = Namespace('http://schema.org/')
COUNCIL = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')

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

    def new_address(self, address):
        addr = al["address/"+address.replace(" ", "_").replace(",","-").lower()]
        self.graph.add((addr, RDF.type, VCARD["Location"]))
        self.graph.add((addr, VCARD['street-address'], Literal(address.split(", ")[0])))
        self.graph.add((addr, VCARD['locality'], Literal(address.split(", ")[1])))
        self.graph.add((addr, POST['postcode'], URIRef("http://data.ordnancesurvey.co.uk/id/postcodeunit/"+address.split(", ")[2].replace(" ",""))))

        self.save()

    def new_allotment(self, address, application, disabled_access, external_link, guidence, location, name, plot_size, rent, Easting, Northing):
        self.new_address(address)
        print utm.from_latlon(float(location.split(',')[0]), float(location.split(',')[1]))[1]
        allotment = al[name.replace(" ", "-").lower()] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/allotment/Allotment')))
        self.graph.add((allotment, COUNCIL['application'], URIRef(application)))
        self.graph.add((allotment, COUNCIL['information'], URIRef(external_link)))
        self.graph.add((allotment, COUNCIL['guidance'], URIRef("http://www.manchester.gov.uk"+guidence)))
        self.graph.add((allotment, GEO["lat"], Literal(location.split(',')[0])))
        self.graph.add((allotment, GEO["long"], Literal(location.split(',')[1])))
        self.graph.add((allotment, OS["northing"], Literal(str(utm.from_latlon(float(location.split(',')[0]), float(location.split(',')[1]))[1]))))
        self.graph.add((allotment, OS["easting"], Literal(str(utm.from_latlon(float(location.split(',')[0]), float(location.split(',')[1]))[0]))))
        self.graph.add((allotment, RDFS['label'], Literal(name)))
        self.graph.add((allotment,VCARD['hasAddress'], URIRef("http://data.gmdsp.org.uk/id/manchester/allotments/address/"+address.replace(" ", "_").replace(",","-").lower())))
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

    reader = csv.DictReader(open('./Data/allotments.csv', mode='rU'))
    for row in reader:
        EASTING, NORTHING, ZONENUMBER, ZONELetter = utm.from_latlon(float(row["Location"].split(',')[0]), float(row["Location"].split(',')[1]))
        s.new_allotment(row["Address"], getURL(row["Application"]), row["Disabled access"], getURL(row["External link"]), getURL(row["Guidance"]), row["Location"], row["Name"], row["Plot sizes"], row["Rent"], EASTING, NORTHING)
        pprint.pprint(row)

if __name__ == '__main__':
    main()
