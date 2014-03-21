#!/usr/bin/env python
import os, csv

from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.store import VALID_STORE

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
    for row in reader:
        allotment = al[utils.idify(row["Name"])]
        graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/allotment')))
        graph.add((allotment, RDFS['label'], Literal(row["Name"])))
        graph.add((allotment, OS["northing"], Literal(row["Northing"])))
        graph.add((allotment, OS["easting"], Literal(row["Easting"])))

        address = utils.idify(row["Address"])
        graph.add((allotment, VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/allotment/address/"+address)))

        # now add the address VCARD
        vcard = al["address/"+address]
        graph.add((vcard, RDF.type, VCARD["location"]))
        graph.add((vcard, VCARD['hasStreetAddress'], Literal(row["Address"])))

        # Now add the statistical data

