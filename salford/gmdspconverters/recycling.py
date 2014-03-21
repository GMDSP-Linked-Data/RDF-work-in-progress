__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

RECYCLING = Namespace('http://data.gmdsp.org.uk/id/salford/recycling-centre/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
    for row in reader:
        rc = RECYCLING[utils.idify(row["UPRN"])]
        graph.add((rc, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/recycling-centre')))
        graph.add((rc, utils.RDFS['label'], Literal(row["Location"])))

        address = utils.idify(row["Address"])
        graph.add((rc, utils.VCARD['adr'], URIRef("http://data.gmdsp.org.uk/def/council/recycling-centre/address/"+address)))

        # now add the address VCARD
        vcard = RECYCLING["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["location"]))
        graph.add((vcard, utils.VCARD['hasStreetAddress'], Literal(row["Address"])))

        # location information
        graph.add((rc, utils.OS["northing"], Literal(row["Northings"])))
        graph.add((rc, utils.OS["easting"], Literal(row["Eastings"])))


        # recycling information
        if row["Cardboard"]:
            graph.add((rc, RECYCLING["hasCardboard"], Literal("true", datatype=XSD.boolean)))
        if row["Paper"]:
            graph.add((rc, RECYCLING["hasPaper"], Literal("true", datatype=XSD.boolean)))
        if row["Cartons"]:
            graph.add((rc, RECYCLING["hasCartons"], Literal("true", datatype=XSD.boolean)))
        if row["Shoes"]:
            graph.add((rc, RECYCLING["hasShoes"], Literal("true", datatype=XSD.boolean)))
        if row["Glass"]:
            graph.add((rc, RECYCLING["hasGlass"], Literal("true", datatype=XSD.boolean)))
        if row["Textiles"]:
            graph.add((rc, RECYCLING["hasTextiles"], Literal("true", datatype=XSD.boolean)))
        if row["Cans"]:
            graph.add((rc, RECYCLING["hasCans"], Literal("true", datatype=XSD.boolean)))
        if row["Foil"]:
            graph.add((rc, RECYCLING["hasFoil"], Literal("true", datatype=XSD.boolean)))
        if row["Plastic Bottles"]:
            graph.add((rc, RECYCLING["hasPlasticBottles"], Literal("true", datatype=XSD.boolean)))
        if row["Aerosols"]:
            graph.add((rc, RECYCLING["hasAerosols"], Literal("true", datatype=XSD.boolean)))

