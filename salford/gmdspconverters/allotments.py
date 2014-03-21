import csv

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

al = Namespace('http://data.gmdsp.org.uk/id/salford/allotments/')
al_stat = Namespace('http://gmdsp.org/def/statistical-dimension/allotments/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
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

        # Now add the statistical data
        stats = al_stat[utils.idify(row["Name"])]
        graph.add((stats, RDF.type, utils.QB['Observation']))
        graph.add((stats, utils.QB["dataSet"], Literal(al)))
        graph.add((stats, al_stat["plots"], Literal(row["Plots"])))

