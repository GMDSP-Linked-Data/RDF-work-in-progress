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

from rdflib import BNode, Graph, URIRef, Literal, Namespace, RDF, XSD
from rdflib.namespace import FOAF, DC

import csv
import pprint
import time

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/spend.turtle'
#storefn = '/home/simon/codes/film.dev/movies.n3'
storeuri = 'file://'+storefn
title = 'Movies viewed by %s'

r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
DIS = Namespace('http://www.w3.org/2006/03/test-description#')
DISSISION = Namespace('http://purl.org/cerif/frapo/')
SUB = Namespace('http://purl.org/dc/terms/')
PAY = Namespace('http://reference.data.gov.uk/def/payment#')
al = Namespace('https://gmdsp-admin.publishmydata.com/id/Planning/')


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
        self.graph.bind('dissision',DISSISION)
        self.graph.bind('sub',SUB)
        self.graph.bind('pay', PAY)

    def save(self):
        print storeuri
        self.graph.serialize(storeuri, format='turtle')

    def new_spend(self, name, type, date, amount, area, supplier, number):
        payment = al[number.replace (" ", "_")] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((payment, RDF.type, PAY.Payment))
        self.graph.add((payment, PAY["reference"], Literal(number)))
        self.graph.add((payment, PAY['payer'], URIRef("http://www.elmbridge.gov.uk/id/"+name.replace(" ","_"))))
        self.graph.add((payment, PAY['payee'], URIRef("http://www.elmbridge.gov.uk/id/payee/"+supplier.replace(" ","_"))))
        self.graph.add((payment, PAY['date'], URIRef('http://reference.data.gov.uk/id/day/'+time.strftime('%Y-%m-%d',date))))
        self.graph.add((payment, PAY['netAmount'], Literal(amount)))
        self.graph.add((payment, PAY['unit'], URIRef("http://www.elmbridge.gov.uk/id/department/"+area.replace(" ","_"))))
        #self.graph.add((allotment, GEO["ward"], Literal(ward)))
        #self.graph.add((allotment, DC['date'], Literal(plot_size)))
        #self.graph.add((allotment, GEO['rating'], Literal(rent)))
        self.save()

def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()

    reader = csv.DictReader(open('./Data/spendover500.csv', mode='r'))
    for row in reader:
        pprint.pprint(row)
        s.new_spend(row["Body Name"], row["Expenses Type"],  time.strptime(row["Invoice Payment Date"], "%d.%m.%Y"), row["Net Amount"][3:], row["Service Area"], row["Supplier Name"], row["Transaction Number"])

if __name__ == '__main__':
    main()