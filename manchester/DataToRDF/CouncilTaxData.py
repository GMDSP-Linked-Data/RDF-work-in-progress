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
from rdflib.namespace import XSD

from itertools import groupby
import csv
import pprint
import utm
from bs4 import BeautifulSoup

storefn = os.path.dirname(os.path.realpath(__file__)) + '/Output/councilTax.rdf'
storen3 = os.path.dirname(os.path.realpath(__file__)) + '/Output/councilTax.ttl'

#storefn = '/home/simon/codes/film.dev/movies.n3'
storeuri = 'file://'+storefn
storeun3 = 'file://'+storen3

title = 'Movies viewed by %s'

r_who = re.compile('^(.*?) <([a-z0-9_-]+(\.[a-z0-9_-]+)*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)>$')

SPACIAL = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
ADMINGEO = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
SCHEME = Namespace('http://schema.org/')
SDMX = Namespace("http://purl.org/linked-data/sdmx#")
SDMXCONCEPT = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
SDMXDIMENSION = Namespace("http://purl.org/linked-data/sdmx/2009/dimension#")
SDMXATTRIBUTE = Namespace("http://purl.org/linked-data/sdmx/2009/attribute#")
SDMXMEASURE= Namespace("http://purl.org/linked-data/sdmx/2009/measure#")
qb = Namespace("http://purl.org/linked-data/cube#")
INTERVAL = Namespace("http://www.w3.org/2006/time#")
COUNCILTAX = Namespace('http://data.gmdsp.org.uk/data/manchester/council-tax/')
DATEREF = Namespace('http://reference.data.gov.uk/id/day/')
COUNCILBAND = Namespace('http://data.gmdsp.org.uk/def/council/Council-Tax/')

class Store:
    def __init__(self):
        self.graph = Graph()

        rt = self.graph.open(storeuri, create=False)
        if rt == None:
            # There is no underlying Sleepycat infrastructure, create it
            self.graph.open(storeuri, create=True)
        else:
            assert rt == VALID_STORE, 'The underlying store is corrupt'

        self.graph.bind('os', POST)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('geo', GEO)
        self.graph.bind('vcard', VCARD)
        self.graph.bind('scheme', SCHEME)
        self.graph.bind('counciltax', COUNCILTAX)
        self.graph.bind('qb', qb)
        self.graph.bind('admingeo',ADMINGEO)
        self.graph.bind('sdmx-attribute', SDMXATTRIBUTE)
        self.graph.bind('interval', INTERVAL)
        self.graph.bind('day', DATEREF)
        self.graph.bind('councilband', COUNCILBAND)

    def save(self):
        #self.graph.serialize(storeuri, format='pretty-xml')
        self.graph.serialize(storeun3, format='n3')

    def new_postcode(self, postcode):
        pc = COUNCILTAX

    def refArea(self):
        d = COUNCILTAX["refArea"]
        self.graph.add((d, RDF.type, qb["Property"]))
        self.graph.add((d, RDF.type, qb["DimensionProperty"]))
        self.graph.add((d, RDFS["label"], Literal("reference area")))
        self.graph.add((d, RDFS["subPropertyOf"], SDMXDIMENSION["refArea"]))
        self.graph.add((d, RDFS["range"], POST["PostcodeArea"]))
        self.graph.add((d, qb["concept"], SDMXCONCEPT["refArea"]))

    def refPeriod(self):
        d = COUNCILTAX["refPeriod"]
        self.graph.add((d, RDF.type, qb["Property"]))
        self.graph.add((d, RDF.type, qb["DimensionProperty"]))
        self.graph.add((d, RDFS["label"], Literal("reference period")))
        self.graph.add((d, RDFS["subPropertyOf"], SDMXDIMENSION["refPeriod"]))
        self.graph.add((d, RDFS["range"], INTERVAL["Interval"]))
        self.graph.add((d, qb["concept"], SDMXCONCEPT["refPeriod"]))

    def refBand(self):
        d = COUNCILTAX["refBand"]
        self.graph.add((d, RDF.type, qb["Property"]))
        self.graph.add((d, RDF.type, qb["DimensionProperty"]))
        self.graph.add((d, RDFS["label"], Literal("reference band")))
        self.graph.add((d, RDFS["domain"], URIRef("http://data.gmdsp.org.uk/def/council/Council-Tax")))

    def countDef(self):
        d = COUNCILTAX["countDef"]
        self.graph.add((d, RDF.type, RDF["Property"]))
        self.graph.add((d, RDF.type, qb["MeasureProperty"]))
        self.graph.add((d, RDFS["label"], Literal("Council tax band count")))
        self.graph.add((d, RDFS["subPropertyOf"], SDMXMEASURE["obsValue"]))
        self.graph.add((d, RDFS["range"], XSD.decimal))

    def new_DSD(self):
        dsd = COUNCILTAX["DSD"]
        self.graph.add((dsd, RDF.type, qb["DataStructureDefinition"]))
        self.graph.add((dsd, qb["dimension"], COUNCILTAX["refArea"]))
        self.graph.add((dsd, qb["dimension"], COUNCILTAX["refPeriod"]))
        self.graph.add((dsd, qb["dimension"], COUNCILTAX["refBand"]))

        self.graph.add((dsd, qb["measure"], COUNCILTAX["countDef"]))

    def new_dataset(self):
        ds = COUNCILTAX["dataset-le1"]
        self.graph.add((ds, RDF.type, qb["DataSet"]))
        self.graph.add((ds, RDFS["label"], Literal("Tax Banding")))
        self.graph.add((ds, RDFS["comment"], Literal("xxxxx")))
        self.graph.add((ds, qb["structure"], COUNCILTAX['data']))

    def new_observation(self, band, postcode, date, count):
        observation = COUNCILTAX[postcode.replace(" ", "-").lower()+band.replace(" ", "-").lower()]
        self.graph.add((observation, RDF.type, qb['Observation']))
        self.graph.add((observation, qb["dataSet"], URIRef('http://data.gmdsp.org.uk/data/manchester/council-tax')))
        self.graph.add((observation, COUNCILTAX['refArea'], URIRef("http://data.ordnancesurvey.co.uk/doc/postcodeunit/"+postcode.replace(" ",""))))
        self.graph.add((observation, COUNCILTAX['countDef'], Literal(count, datatype=XSD.integer)))
        #refrence this to the list in the data set which Ian is making.
        self.graph.add((observation, COUNCILTAX['refBand'], COUNCILBAND[band]))
        self.graph.add((observation, COUNCILTAX['refPeriod'], DATEREF[time.strftime('%Y-%m-%d',date)]))


def keyfn(x):
    return x['Postcode']

def keyfnp(x):
    return x['Band']


def main(argv=None):
    s = Store()
    s.refPeriod()
    s.refArea()
    s.refBand()
    s.countDef()
    s.new_dataset()
    #s.new_DSD()

    count = 0

    reader = csv.DictReader(open('./Data/Ctax Extract.csv', mode='rU'))
    for k,g in [(k, list(g)) for k,g in groupby(sorted(reader, key=keyfn), keyfn)]:
        for b,n in [(kq, list(go)) for kq,go in groupby(sorted(g, key=keyfnp), keyfnp)]:
            if count <= 1000000:
                s.new_observation(b, k, time.strptime("01/01/0001", "%d/%m/%Y"), len(n))
                count = count + 1
    print "-- Saving --"
    s.save()

if __name__ == '__main__':
    main()