import csv
import os

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_stat = Namespace('http://gmdsp.org/def/statistical-dimension/allotments/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    # set up a separate graph for the statistics
    # TODO: set up generic way of creating statistics, this is very hardecody!
    statistics_graph = utils.create_graph()

    for row in reader:
        allotment = al[utils.idify(row["Name"])]
        graph.add((allotment, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/allotment')))
        graph.add((allotment, utils.RDFS['label'], Literal(row["Name"])))
        graph.add((allotment, utils.OS["northing"], Literal(row["Northing"])))
        graph.add((allotment, utils.OS["easting"], Literal(row["Easting"])))

        address = utils.idify(row["Address"])
        graph.add((allotment, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/allotment/address/"+address)))

        # now add the address VCARD
        vcard = al["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.VCARD['hasStreetAddress'], Literal(row["Address"])))

        if row["Plots"]:
            try:
                statistics_graph.add((allotment, al_stat["plots"], Literal(int(row["Plots"]), datatype=XSD.integer)))
                statistics_graph.add((allotment, RDF.type, utils.QB['Observation']))
                statistics_graph.add((allotment, utils.QB["dataSet"], Literal(al)))
                statistics_graph.add((allotment, al_stat["statistics"], allotment))
            except ValueError:
                pass

    utils.output_graph(statistics_graph, os.path.join("output", "allotments2014Q4.rdf"))


def statistics(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        allotment = al[utils.idify(row["Name"])]