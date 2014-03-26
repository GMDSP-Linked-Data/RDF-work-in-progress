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
        graph.add((p, RDF.type, PARKING_ONT["ParkingSite"]))
        graph.add((p, utils.RDFS['label'], Literal(row["Name"])))
        graph.add((p, PARKING_ONT['type'], Literal(row["Type"])))
        graph.add((p, PARKING_ONT['informationPage'], Literal(row["URL"])))

        p_operator = PARKING["operator/" + utils.idify(row["Operator"])]
        graph.add((p, PARKING_ONT['operator'], p_operator))
        graph.add((p_operator, RDF.type, PARKING_ONT["ParkingSiteOperator"]))
        graph.add((p_operator, utils.RDFS['label'], Literal(row["Operator"])))
        graph.add((p_operator, utils.ADMINGEO["MetropolitanDistrict"], URIRef("http://data.ordnancesurvey.co.uk/id/7000000000018805")))

        graph.add((p, utils.GEO["lat"], Literal(row["Latitude"])))
        graph.add((p, utils.GEO["long"], Literal(row["Longitude"])))

        address = utils.idify(row["Address"])
        graph.add((p, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/parking/address/"+address)))

        # now add the address VCARD
        vcard = PARKING["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.RDFS['label'], Literal(row["Name"])))
        graph.add((vcard, utils.VCARD['street-address'], Literal(row["Address"])))
        graph.add((vcard, utils.VCARD['postal-code'], Literal(row["Postcode"])))
