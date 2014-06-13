__author__ = 'jond'

import csv
import re

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

STREETLIGHT = Namespace('http://data.gmdsp.org.uk/id/salford/streetlighting/')
STREETLIGHT_ONT = Namespace('http://data.gmdsp.org.uk/def/council/streetlighting/')


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        if row["FEATURE ID"]:
            sl = STREETLIGHT[utils.idify(row["FEATURE ID"])]
            graph.add((sl, RDF.type, STREETLIGHT_ONT["Streetlight"]))
            graph.add((sl, utils.RDFS['label'], Literal("Streetlight with ID " + row["FEATURE ID"])))

            address = utils.idify(row["FEATURE ID"])
            graph.add((sl, utils.VCARD['hasAddress'], STREETLIGHT["address/"+address]))

            # now add the address VCARD
            vcard = STREETLIGHT["address/"+address]
            graph.add((vcard, RDF.type, utils.VCARD["Location"]))
            graph.add((vcard, utils.RDFS['label'], Literal("Address of streetlight with ID " + row["FEATURE ID"])))
            graph.add((vcard, utils.VCARD['street-address'], Literal(row["ROADNAME"])))
            graph.add((vcard, utils.VCARD['postal-code'], Literal(row["POSTCODE"])))
            graph.add((vcard, utils.POST['postcode'], URIRef(utils.convertpostcodeto_osuri(row["POSTCODE"]))))

            # location information
            graph.add((sl, utils.OS["northing"], Literal(row["Northings"])))
            graph.add((sl, utils.OS["easting"], Literal(row["Eastings"])))
            # add conversion for lat/long
            lat_long = utils.ENtoLL84(float(row["Eastings"]), float(row["Northings"]))
            graph.add((sl, utils.GEO["long"], Literal(lat_long[0])))
            graph.add((sl, utils.GEO["lat"], Literal(lat_long[1])))

            # street light specific stuff
            if row["LAMP WATTAGE"]:
                watts = re.findall('\d+', row["LAMP WATTAGE"])[0]
                graph.add((sl, STREETLIGHT_ONT['wattage'], Literal(watts)))
            graph.add((sl, STREETLIGHT_ONT['lampType'], Literal(row["LAMP TYPE"])))

            if row["Mounting Height                                  "]:
                height = re.findall('\d+', row["Mounting Height                                  "])[0]
                graph.add((sl, STREETLIGHT_ONT['columnHeight'], Literal(height)))



