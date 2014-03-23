__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

PARKING = Namespace('http://data.gmdsp.org.uk/id/salford/parking/')
PARKING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/parking/')

def convert(graph, input_path):
    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        p = PARKING[utils.idify(row["Name"])]
        graph.add((p, RDF.type, PARKING_ONT["Parking"]))
        graph.add((p, utils.RDFS['label'], row["Name"]))
        graph.add((p, PARKING_ONT['type'], row["Type"]))
        graph.add((p, PARKING_ONT['operator'], row["Operator"]))

        address = utils.idify(row["Address"])
        graph.add((p, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/parking/address/"+address)))

        # now add the address VCARD
        vcard = PARKING["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.VCARD['street-address'], Literal(row["Address"])))
        graph.add((vcard, utils.VCARD['postal-code'], Literal(row["Postcode"])))
