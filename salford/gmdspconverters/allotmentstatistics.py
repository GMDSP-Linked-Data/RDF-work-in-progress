import csv
import os
import re

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_ont = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')
al_stat = Namespace('http://gmdsp.org/def/statistical-dimension/allotments/')

YEAR_STRING = "2013-Q4"


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    for row in reader:
        allotment = al[utils.idify(row["Name"])]

        if row["Plots"]:
            try:
                graph.add((allotment, utils.RDFS['label'], Literal("{}, {}, number of plots".format(row["Name"], YEAR_STRING))))
                graph.add((allotment, al_ont["numberOfPlots"], Literal(int(row["Plots"]), datatype=XSD.integer)))
                graph.add((allotment, RDF.type, utils.QB['Observation']))
            except ValueError:
                pass
