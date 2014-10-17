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
import BeautifulSoup

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/allotments-stockport.rdf'
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
        print '1'

        #self.new_address(address)
        print '2'
        #print utm.from_latlon(float(location.split(',')[0]), float(location.split(',')[1]))[1]

        allotment = al[name.replace(" ", "-").lower()] # @@ humanize the identifier (something like #rev-$date)
        print '3'
        self.graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/allotment/Allotment')))
        self.graph.add((allotment, COUNCIL['application'], URIRef(application)))
        self.graph.add((allotment, COUNCIL['information'], URIRef(external_link)))
        print '3'
        self.graph.add((allotment, COUNCIL['guidance'], URIRef("http://www.manchester.gov.uk"+guidence)))
       # self.graph.add((allotment, GEO["lat"], Literal(location.split(',')[0])))
        print '4'
       # self.graph.add((allotment, GEO["long"], Literal(location.split(',')[1])))
        print '4'
        self.graph.add((allotment, OS["northing"], Literal(Easting)))
        self.graph.add((allotment, OS["easting"],  Literal(Northing)))
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

    tree = ET.parse('./Data/Allotments.xml')
    root = tree.getroot()
    for child in root:
        #for each street light
        for c in child:
            #for each atribute in street light
            try:
                print " -------- "
                print c[0].tag
                print c[0].text #site code
                print c[1].tag
                print c[1].text#feature group name
                print c[2].tag
                print c[2].text#site_id
                print c[3].tag
                print c[3].text#site_name
                print c[4].tag
                print c[4].text#feature_id
                print c[5].tag
                print c[5].text#class
                print c[6].tag
                print c[6].text#area
                print c[7].tag
                print c[7].text#slc_typology
                print c[8].tag
                print c[8].text#fContract_Area
                print c[9].tag
                print c[9].text#eastigng
                print c[10].tag
                print c[10].text#northing

                #def new_allotment(self, address, application, disabled_access, external_link, guidence, location, name, plot_size, rent, Easting, Northing):

                #s.new_allotment(0, '', c[9].text, c[3].text, c[0].text, c[1].text, 0)
                #s.new_allotment(0,0,0,0,0,0,0, c[3].text,0,0,c[9].text, c[10].text)

                s.new_allotment("","","","","","", c[3].text,"","",c[9].text, c[10].text)


            except:
                print "Unexpected error:", sys.exc_info()
    s.save()

if __name__ == '__main__':
    main()