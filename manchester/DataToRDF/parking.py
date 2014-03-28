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
import shapefile

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

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/parking.ttl'
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
sl = Namespace('https://gmdsp-admin.publishmydata.com/id/manchester/gritting/')

PARKING = Namespace('http://data.gmdsp.org.uk/id/manchester/parking/')
PARKING_ONT = Namespace('http://data.gmdsp.org.uk/def/manchester/parking/')

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

    def save(self):
        self.graph.serialize(storeuri, format='turtle')

    def new_park(self, row):
        p = PARKING[row["Name"].replace(" ", "-").replace(",", "")]
        self.graph.add((p, RDF.type, PARKING_ONT["ParkingSite"]))
        self.graph.add((p, RDFS['label'], Literal(row["Name"])))
        self.graph.add((p, PARKING_ONT['type'], URIRef('http://data.gmdsp.org.uk/def/council/parking/parking-type/'+row["Type"].replace(" ", "-").replace(",", ""))))

        p_operator = PARKING["operator/" + row["Run by"].replace(" ", "-").replace(",", "")]
        self.graph.add((p, PARKING_ONT['operator'], p_operator))
        self.graph.add((p_operator, RDF.type, PARKING_ONT["ParkingSiteOperator"]))
        self.graph.add((p_operator, RDFS['label'], Literal(row["Run by"])))
        self.graph.add((p_operator, OS["MetropolitanDistrict"], URIRef("http://data.ordnancesurvey.co.uk/id/7000000000018821")))

        self.graph.add((p, GEO["lat"], Literal(row["Location"].split(",")[0])))
        self.graph.add((p, GEO["long"], Literal(row["Location"].split(",")[1])))

        address = row["Address"]
        self.graph.add((p, VCARD['hasAddress'], URIRef("http://data.gmdsp.org.uk/def/council/parking/address/"+address.replace(" ", "-").replace(",", ""))))

        # now add the address VCARD
        vcard = PARKING["address/"+address.replace(" ", "-").replace(",", "")]
        self.graph.add((vcard, RDF.type, VCARD["Location"]))
        self.graph.add((vcard, RDFS['label'], Literal(row["Name"])))
        self.graph.add((vcard, VCARD['street-address'], Literal(row["Address"])))
        #self.graph.add((vcard, VCARD['postal-code'], Literal(row["Postcode"])))
        #self.graph.add((vcard, POST['postcode'], URIRef(utils.convertpostcodeto_osuri(row["Postcode"]))))

def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()


    reader = csv.DictReader(open('./Data/parking2.csv', mode='rU'))
    for row in reader:
        s.new_park(row)
        pprint.pprint(row)
    s.save()

if __name__ == '__main__':
    main()