#!/usr/bin/env python
import os, csv

from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.store import VALID_STORE

storefn = os.path.dirname(os.path.realpath(__file__)) + '/allotments-tmp.rdf'
storeuri = 'file://'+storefn

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
SCHEME = Namespace('http://schema.org/')

graph = Graph()

rt = graph.open(storeuri, create=False)
if rt == None:
    # There is no underlying Sleepycat infrastructure, create it
    graph.open(storeuri, create=True)
else:
    assert rt == VALID_STORE, 'The underlying store is corrupt'

graph.bind('os', OS)
graph.bind('rdfs', RDFS)
graph.bind('geo', GEO)
graph.bind('vcard', VCARD)
graph.bind('scheme', SCHEME)

reader = csv.DictReader(open('../sourcedata/allotments/allotments.csv', mode='r'))
for row in reader:
    allotment = al[row["Name"].replace(" ", "-").lower()] # @@ humanize the identifier (something like #rev-$date)
    graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/allotment')))
    graph.add((allotment, RDFS['label'], Literal(row["Name"])))
    graph.add((allotment, OS["northing"], Literal(row["Northing"])))
    graph.add((allotment, OS["easting"], Literal(row["Easting"])))

    address = row["Address"]
    graph.add((allotment, VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/allotment/address/"+address.replace(" ", "_").replace(",","-").lower())))

    # now add the address VCARD
    vcard = al["address/"+address.replace(" ", "_").replace(",","-").lower()]
    graph.add((vcard, RDF.type, VCARD["location"]))
    graph.add((vcard, VCARD['hasStreetAddress'], Literal(row["Address"])))

    # Now add the statistical data

graph.serialize(storeuri, format='pretty-xml')