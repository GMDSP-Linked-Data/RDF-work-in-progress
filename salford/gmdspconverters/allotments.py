import csv
import os
import re

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_ont = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')
al_stat = Namespace('http://gmdsp.org/def/statistical-dimension/allotments/')


def postcode_helper(addr_string):
    """
    Tries to get the postcode out of the given string, assuming it is at the end of the string
    Returns 2 strings, the 1st string is the street address, the 2nd is the postcode. If it
    can't find the postcode then it returns None
    """
    #regex from #http://en.wikipedia.orgwikiUK_postcodes#Validation
    postcode = re.findall(r'[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}', addr_string)
    if postcode:
        return addr_string.split(postcode[0])[0], postcode[0]
    return addr_string, None


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    # set up a separate graph for the statistics
    # TODO: set up generic way of creating statistics, this is very hardecody!
    statistics_graph = utils.create_graph()

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

        street_address, address_postcode = postcode_helper(row["Address"])

        # now add the address VCARD
        vcard = al["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["Location"]))
        graph.add((vcard, utils.RDFS['label'], Literal("Address of allotment site " + row["Name"])))
        graph.add((vcard, utils.VCARD['street-address'], Literal(street_address)))
        if address_postcode is not None:
            graph.add((vcard, utils.VCARD['postal-code'], Literal(address_postcode)))
            graph.add((vcard, utils.POST['postcode'], URIRef(utils.convertpostcodeto_osuri(address_postcode))))

        if row["Plots"]:
            try:
                statistics_graph.add((allotment, al_stat["plots"], Literal(int(row["Plots"]), datatype=XSD.integer)))
                statistics_graph.add((allotment, RDF.type, utils.QB['Observation']))
                statistics_graph.add((allotment, utils.QB["dataSet"], Literal(al)))
                statistics_graph.add((allotment, al_stat["statistics"], allotment))
            except ValueError:
                pass

    utils.output_graph(statistics_graph, os.path.join("output", "allotments2014Q4.rdf"))
