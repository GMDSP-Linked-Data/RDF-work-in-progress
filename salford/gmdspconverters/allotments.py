import csv
import re

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_ont = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        allotment = al[utils.idify(row["Name"])]
        graph.add((allotment, RDF.type, al_ont['Allotment']))
        graph.add((allotment, utils.RDFS['label'], Literal("Allotment site " + row["Name"])))

        # geo info
        graph.add((allotment, utils.OS["northing"], Literal(row["Northing"])))
        graph.add((allotment, utils.OS["easting"], Literal(row["Easting"])))
        # add conversion for lat/long
        lat_long = utils.ENtoLL84(float(row["Easting"]), float(row["Northing"]))
        graph.add((allotment, utils.GEO["long"], Literal(lat_long[0])))
        graph.add((allotment, utils.GEO["lat"], Literal(lat_long[1])))

        address = utils.idify(row["Address"])
        graph.add((allotment, utils.VCARD['hasAddress'], al["address/"+address]))

        street_address, address_postcode = utils.postcode_helper(row["Address"])

        # now add the address VCARD
        vcard = al["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["Location"]))
        graph.add((vcard, utils.RDFS['label'], Literal("Address of allotment site " + row["Name"])))
        graph.add((vcard, utils.VCARD['street-address'], Literal(street_address)))
        if address_postcode is not None:
            graph.add((vcard, utils.VCARD['postal-code'], Literal(address_postcode)))
            graph.add((vcard, utils.POST['postcode'], URIRef(utils.convertpostcodeto_osuri(address_postcode))))
