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

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/planning.rdf'
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
PLUREL = Namespace('http://purl.org/cerif/frapo/')
PLANNING = Namespace('http://data.gmdsp.org.uk/def/council/planning/')
PLANNINGID = Namespace('http://data.gmdsp.org.uk/id/manchester/planning/')

class Store:
    def __init__(self):
        self.graph = Graph()
        self.disc = []
        self.applic = []
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
        self.graph.bind('planing', PLANNING)
        self.graph.bind('plurel', PLUREL)
        self.graph.bind('id', PLANNINGID)

    def save(self):
        self.graph.serialize(storeuri, format='pretty-xml')

    #def new_allotment(self, address, dateapval, datdeciss, code_codetext, decsn_code, dtypnumbco, refval, plot_size, ward):
    def new_plan(self, address, ward, refval, dateapval, datdeciss, dissision, application_type, proposal, DTYPNUMBCO_CODETEXT):
        if dissision not in self.disc:
            print dissision
            self.new_dission(dissision)
            self.disc.append(dissision)

        if application_type not in self.applic:
            print application_type
        #     self.new_application_type(application_type)
            self.applic.append(application_type)

        applicatinon = PLANNINGID[refval.replace ("/", "-").lower()] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((applicatinon, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/planning/PlanningApplication')))
        self.graph.add((applicatinon, VCARD['street-address'], Literal(address)))
        self.graph.add((applicatinon, PLANNING['decisionDate'], URIRef('http://reference.data.gov.uk/id/day/'+time.strftime('%Y-%m-%d',datdeciss))))
        self.graph.add((applicatinon, PLANNING['validatedDate'], URIRef('http://reference.data.gov.uk/id/day/'+time.strftime('%Y-%m-%d',dateapval))))
        self.graph.add((applicatinon, PLANNING['decision'], URIRef('http://data.gmdsp.org.uk/def/council/planning/planning-application-status/'+dissision.replace (" ", "-").lower())))
        self.graph.add((applicatinon, PLANNING['applicationType'], URIRef('http://data.gmdsp.org.uk/def/council/planning/planning-application-status/'+application_type.replace (" ", "-").lower())))
        self.graph.add((applicatinon, OS["DistrictWard"], URIRef("http://data.ordnancesurvey.co.uk/id/"+ward)))
        self.graph.add((applicatinon, PLANNING["proposal"], Literal(proposal)))
        self.graph.add((applicatinon, PLANNING["other"], Literal(DTYPNUMBCO_CODETEXT)))

    def new_dission(self, dissision):
        dissision = PLANNINGID[dissision.replace (" ", "-").lower()]
        self.graph.add((dissision, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/planning/decision')))
        self.graph.add((dissision, RDFS["label"], Literal(dissision)))

    def new_application_type(self, aplication_type):
        application_type = PLANNINGID[aplication_type.replace (" ", "-").lower()]
        self.graph.add((application_type, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/neighbourhood/planning/application-type')))
        self.graph.add((application_type, RDFS["label"], Literal(aplication_type)))

def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()
    rx = re.compile('\W+')
    reader = csv.DictReader(open('./Data/planning2.csv', mode='rU'))
    count = 0
    for row in reader:
        #s.new_allotment(row["Address"], row["Application"], row["Disabled access"], row["External link"], row["Guidance"], row["Location"], row["Name"], row["Plot sizes"], row["Rent"])
        if row["DATEDECISS"] == "":
            row["DATEDECISS"] = "01/01/0001"

        if row["DATEAPVAL"] == "":
            row["DATEAPVAL"] = "01/01/0001"

        if count < 10000000000:
            count = count + 1
            s.new_plan(rx.sub(" ", row["ADDRESS"]).strip(), row["Ward Name"].strip().replace(' ','-'), row["REFVAL"].strip(), time.strptime(row["DATEAPVAL"].strip(), "%d/%m/%Y"), time.strptime(row["DATEDECISS"].strip(), "%d/%m/%Y"), row["DECSN CODE_CODETEXT"], row["DCAPPTYP CODE_CODETEXT"], rx.sub(" ", row["PROPOSAL"]).strip().decode("utf-8", "replace").replace('\n', ' ').replace('\r', ''), row["DTYPNUMBCO_CODETEXT"])
    s.save()

if __name__ == '__main__':
    main()