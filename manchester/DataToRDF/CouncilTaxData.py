__author__ = 'danielkershaw'
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

from itertools import groupby
import csv
import pprint
import utm
from bs4 import BeautifulSoup

storefn = os.path.dirname(os.path.realpath(__file__)) + '/allotments-tmp.rdf'
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

def keyfn(x):
    return x['Postcode']

def keyfnp(x):
    return x['Band']


def main(argv=None):
    s = Store()

    reader = csv.DictReader(open('./Data/Ctax Extract.csv', mode='rU'))
    # for row in reader:
    #     pprint.pprint(row)
    group = [(k, list(g)) for k,g in groupby(sorted(reader, key=keyfn), keyfn)]
    for k,g in group:
        #print k
        for b,n in [(kq, list(go)) for kq,go in groupby(sorted(g, key=keyfnp), keyfnp)]:
            print "{0}, {1}, {2}".format(k, b, len(n))

if __name__ == '__main__':
    main()