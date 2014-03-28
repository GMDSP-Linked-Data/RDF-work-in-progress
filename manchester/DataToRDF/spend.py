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

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/spend-tmp.rdf'
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
payee = Namespace('http://data.gmdsp.org.uk/id/manchester/payee/')
payer = Namespace('http://data.gmdsp.org.uk/id/manchester/payer/')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
org = Namespace('http://www.w3.org/ns/org#')
owl = Namespace('http://www.w3.org/2002/07/owl#')
qb = Namespace("http://purl.org/linked-data/cube#")
void = Namespace('http://vocab.deri.ie/void#')
opmv = Namespace('http://purl.org/net/opmv/ns#')

payline = Namespace('http://data.gmdsp.org.uk/id/manchester/')
gmdsp = Namespace('http://data.gmdsp.org.uk/id/')
department = Namespace('http://data.gmdsp.org.uk/id/manchester/department/')
al = Namespace('http://data.gmdsp.org.uk/id/manchester/payment/')
payline = Namespace('http://data.gmdsp.org.uk/id/manchester/public/')
invoice = Namespace('http://data.gmdsp.org.uk/id/manchester/invoice')
class Store:
    def __init__(self):
        self.graph = Graph()
        self.expendituerlinecount = 0
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
        self.graph.bind('payee', payee)
        self.graph.bind('payer', payer)
        self.graph.bind('foaf', foaf)
        self.graph.bind('org', org)
        self.graph.bind('qb', qb)
        self.graph.bind('owl', owl)
        self.graph.bind('department', department)
        self.graph.bind('payline', payline)
        self.graph.bind('void', void)
        self.graph.bind('opmv', opmv)
        self.graph.bind('invoice', invoice)
    def save(self):
        print storeuri
        self.graph.serialize(storeuri, format='pretty-xml')

    def new_payline(self, amount, paylinename, id):
        line = payline[paylinename+"/expenditure"+str(self.expendituerlinecount)]

        self.graph.add((line, RDF.type, PAY["ExpenditureLine"]))
        self.graph.add((line, RDFS.label, Literal('Expenditure Line '+str(self.expendituerlinecount), lang='en')))
        self.graph.add((line, qb.dataSet, payline[paylinename]))
        self.graph.add((line, PAY['payment'], al[id.replace(" ","-")]))
        if PAY['netAmount'] == ',':
            self.graph.add((line, PAY['netAmount'], Literal(amount[-1:])))
        else:
            self.graph.add((line, PAY['netAmount'], Literal(amount)))
        self.expendituerlinecount = self.expendituerlinecount + 1

    def new_FormalOrganization(self):
        g = gmdsp["manchester"]
        self.graph.add((g, RDF.type, org.FormalOrganization))
        self.graph.add((g, owl.sameAs, URIRef('http://statistics.data.gov.uk/id/local-authority/00BN')))
        self.graph.add((g, RDFS.label, Literal("Manchester", lang='en')))

    def new_OrganizationalUnit(self, name):
        unit = department[name.replace(" ","-")]
        self.graph.add((unit, RDF.type, org.OrganizationalUnit))
        self.graph.add((unit, org.unitOf, gmdsp["manchester"]))
        self.graph.add((unit, RDFS.label, Literal(name, lang='en')))

        council = gmdsp["manchester"]
        self.graph.add((council, org.hasUnit, unit))


    def new_payee(self, name):
        payment = payee[name.replace(" ", "-")] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((payment, RDF.type, org["Organization"]))
        self.graph.add((payment, RDFS["label"], Literal(name, lang='en')))

    def new_spend(self, name, type, date, amount, area, supplier, number):
        self.new_payee(supplier)
        self.new_FormalOrganization()
        self.new_OrganizationalUnit(area)

        payment = al[number.replace(" ", "-")] # @@ humanize the identifier (something like #rev-$date)
        self.graph.add((payment, RDF.type, PAY.Payment))
        self.graph.add((payment, RDFS.label, Literal("Invoice"+number, lang='en')))
        self.graph.add((payment, PAY["reference"], Literal(number)))
        self.graph.add((payment, PAY['payer'], URIRef('http://data.gmdsp.org.uk/id/manchester')))
        self.graph.add((payment, PAY['payee'], URIRef('http://data.gmdsp.org.uk/id/manchester/payee/'+supplier.replace(" ","-"))))
        self.graph.add((payment, PAY['date'], URIRef('http://reference.data.gov.uk/id/day/'+time.strftime('%Y-%m-%d',date))))
        self.graph.add((payment, PAY['unit'], URIRef('http://data.gmdsp.org.uk/id/manchester/department/'+area.replace(" ","-"))))
        pprint.pprint(payline["finance_line_level_data_01042009-31032010/expenditure"+str(self.expendituerlinecount)])
        self.graph.add((payment, PAY['expenditureLine'], payline["finance_line_level_data_01042009-31032010/expenditure"+str(self.expendituerlinecount)]))
        self.new_payline(amount, "finance_line_level_data_01042009-31032010", number)
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], qb.slice, payment))

    def define_dataset(self):
        dataset = gmdsp['expenditure']
        self.graph.add((dataset, RDF.type, void['Dataset']))
        self.graph.add((dataset, void.subset,  payline["finance_line_level_data_01042009-31032010"]))

        self.graph.add((payline["finance_line_level_data_01042009-31032010"], RDF.type, PAY['PaymentDataset']))
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], RDF.type, void.Dataset))
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], RDF.type, opmv.Artifact))


        # Cube structure (statistical metadata)
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], qb.structure, PAY["payments-with-expenditure-structure"]))
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], PAY.currency, URIRef("http://dbpedia.org/resource/Pound_sterling")))
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], qb.sliceKey, PAY["payment-slice"]))

        self.graph.add((payline["finance_line_level_data_01042009-31032010"], void.vocabulary, PAY['']))
        self.graph.add((payline["finance_line_level_data_01042009-31032010"], void.vocabulary, qb['']))

def help():
    print(__doc__.split('--')[1])

def main(argv=None):
    s = Store()
    s.define_dataset()
    reader = csv.DictReader(open('./Data/spendover500.csv', mode='r'))
    for row in reader:
        #pprint.pprint(row)
        s.new_spend(row["Body Name"], row["Expenses Type"],  time.strptime(row["Invoice Payment Date"], "%d.%m.%Y"), row["Net Amount"][3:], row["Service Area"], row["Supplier Name"], row["Transaction Number"])
    s.save()
if __name__ == '__main__':
    main()