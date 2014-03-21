__author__ = 'jond'

import csv
import re

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/street-lights/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        sl = al[utils.idify(row["FEATURE ID"])]
        graph.add((sl, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/streetlighting')))
        graph.add((sl, utils.RDFS['label'], Literal(row["FEATURE ID"])))

        address = utils.idify(row["FEATURE ID"])
        graph.add((sl, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/streetlighting/address/"+address)))

        # now add the address VCARD
        vcard = al["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.VCARD['street-address'], Literal(row["ROADNAME"])))
        graph.add((vcard, utils.VCARD['postal-code'], Literal(row["POSTCODE"])))

        # street light specific stuff
        if row["LAMP WATTAGE"]:
            watts = re.findall('\d+', row["LAMP WATTAGE"])[0]
            graph.add((sl, al['wattage'], Literal(watts)))
        graph.add((sl, al['lampType'], Literal(row["LAMP TYPE"])))

        if row["Mounting Height                                  "]:
            height = re.findall('\d+', row["Mounting Height                                  "])[0]
            graph.add((sl, al['columnHeight'], Literal(height)))



