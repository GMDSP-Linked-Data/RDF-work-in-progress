import csv

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_ont = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')
al_stat = Namespace('http://gmdsp.org/def/statistical-dimension/allotments/')
number_of_plots = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/allotment-stats/number-of-plots/')

YEAR_STRING = "2013-Q4"


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    # define time reference data
    graph.add((utils.QUARTER[YEAR_STRING], RDF.type, utils.QB["DimensionProperty"]))
    graph.add((utils.QUARTER[YEAR_STRING], utils.RDFS["label"], Literal("2013 Q4")))

    for row in reader:
        if row["Plots"]:
            try:
                Literal(int(row["Plots"])) # figure out if there is any plot data before we start adding data
                allotment_plots = number_of_plots[YEAR_STRING + "/" + utils.idify(row["Name"])]
                graph.add((allotment_plots, utils.RDFS['label'], Literal("{}, {}, number of plots".format(row["Name"], YEAR_STRING))))
                graph.add((allotment_plots, al_ont["numberOfPlots"], Literal(int(row["Plots"]), datatype=XSD.integer)))
                graph.add((allotment_plots, RDF.type, utils.QB['Observation']))
            except ValueError:
                pass
