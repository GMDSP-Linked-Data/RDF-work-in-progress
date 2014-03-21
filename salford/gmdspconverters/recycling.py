__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

RECYCLING = Namespace('http://data.gmdsp.org.uk/id/salford/recyclingsites/')
GMDSP = Namespace('http://data.gmdsp.org.uk/def/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
    for row in reader:
        rc = RECYCLING[utils.idify(row["Location"])]
        graph.add((rc, RDF.type, URIRef('http://data.gmdsp.org.uk/def/recyclingsites')))
        graph.add((rc, utils.RDFS['label'], Literal(row["Location"])))

        address = utils.idify(row["Address"])
        graph.add((rc, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/recycling-centre/address/"+address)))

        # now add the address VCARD
        vcard = RECYCLING["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.VCARD['street-address'], Literal(row["Address"])))

        # location information
        graph.add((rc, utils.OS["northing"], Literal(row["Northings"])))
        graph.add((rc, utils.OS["easting"], Literal(row["Eastings"])))


        # recycling information

        # maps the CSV header to the recycling facility concept schema
        facility_map = {
            "Cardboard": "Cardboard",
            "Paper": "Paper",
            "Cartons": "Cartons",
            "Shoes": "Shoes",
            "Glass": "Glass",
            "Textiles": "Textiles",
            "Cans": "Cans",
            "Plastic Bottles": "Plastic",
            "Aerosols": "Aerosols",
        }

        for facility in facility_map:
            if row[facility]:
                graph.add((rc, GMDSP['facility'], Literal(facility_map[facility])))
