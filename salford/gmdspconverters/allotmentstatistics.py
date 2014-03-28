import csv

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_ont = Namespace('http://data.gmdsp.org.uk/def/council/allotment/')
al_stat = Namespace('http://data.gmdsp.org.uk/def/statistical-dimension/allotments/')
al_data = Namespace('http://data.gmdsp.org.uk/data/salford/allotments/')
number_of_plots = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/allotment-stats/number-of-plots/')

YEAR_STRING = "2013-Q4"


def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))

    # define time reference data ontology
    #graph.add((utils.QUARTER[YEAR_STRING], RDF.type, utils.QB["DimensionProperty"]))
    #graph.add((utils.QUARTER[YEAR_STRING], utils.RDFS["label"], Literal("2013 Q4")))
    refperiod = al_ont["refPeriod"]
    graph.add((refperiod, RDF.type, utils.QB["DimensionProperty"]))
    graph.add((refperiod, utils.RDFS["label"], Literal("Reference period")))
    graph.add((refperiod, utils.RDFS["subPropertyOf"], utils.SDMXDIMENSION["refPeriod"]))
    graph.add((refperiod, utils.RDFS["range"], utils.INTERVAL["Interval"]))
    graph.add((refperiod, utils.QB["concept"], utils.SDMXCONCEPT["refPeriod"]))


    # define number of plots ontology
    #graph.add((al_ont["numberOfPlots"], RDF.type, utils.QB["MeasureProperty"]))
    #graph.add((al_ont["numberOfPlots"], utils.RDFS["label"], Literal("Total number of plots")))
    numberofplots = al_ont["numberOfPlots"]
    graph.add((numberofplots, RDF.type, utils.QB["MeasureProperty"]))
    graph.add((numberofplots, utils.RDFS["label"], Literal("Total number of plots")))
    graph.add((numberofplots, utils.RDFS["subPropertyOf"], utils.SDMXMEASURE["obsValue"]))
    graph.add((numberofplots, utils.RDFS["range"], XSD.integer))

    # add the dataset
    dataset = al_data["dataset-le1"]
    graph.add((dataset, RDF.type, utils.QB["DataSet"]))
    graph.add((dataset, utils.RDFS["label"], Literal("Number of plots in allotment")))
    graph.add((dataset, utils.RDFS["comment"], Literal("xxxxx")))
    graph.add((dataset, utils.QB["structure"], al_data['data']))

    # now add the observations themselves
    for row in reader:
        if row["Plots"]:
            try:
                Literal(int(row["Plots"])) # figure out if there is any plot data before we start adding data

                allotment = al_data[utils.idify(row["Name"])]
                #graph.add((allotment, utils.QB['DimensionProperty'], al_ont["numberOfPlots"]))

                allotment_plots = number_of_plots[YEAR_STRING + "/" + utils.idify(row["Name"])]
                graph.add((allotment_plots, RDF.type, utils.QB['Observation']))
                graph.add((allotment_plots, utils.QB['dataSet'], URIRef(al_data)))
                graph.add((allotment_plots, al_ont["numberOfPlots"], Literal(int(row["Plots"]), datatype=XSD.integer)))
                graph.add((allotment_plots, al_ont["refPeriod"], utils.QUARTER[YEAR_STRING]))
                graph.add((allotment_plots, utils.RDFS['label'], Literal("{}, {}, number of plots".format(row["Name"], YEAR_STRING))))
                graph.add((allotment_plots, al_stat['refAllotment'], allotment))
            except ValueError:
                pass

