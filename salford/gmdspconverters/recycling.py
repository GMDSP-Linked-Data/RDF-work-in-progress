__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF

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

        """
        # recycling information
        graph << [subject, RECYCLING_CENTRES.hasCardboard, csv_obj["Cardboard"]] unless csv_obj["Cardboard"].nil?
        graph << [subject, RECYCLING_CENTRES.hasPaper, csv_obj["Paper"]] unless csv_obj["Paper"].nil?
        graph << [subject, RECYCLING_CENTRES.hasCartons, csv_obj["Cartons"]] unless csv_obj["Cartons"].nil?
        graph << [subject, RECYCLING_CENTRES.hasShoes, csv_obj["Shoes"]] unless csv_obj["Shoes"].nil?
        graph << [subject, RECYCLING_CENTRES.hasGlass, csv_obj["Glass"]] unless csv_obj["Glass"].nil?
        graph << [subject, RECYCLING_CENTRES.hasTextiles, csv_obj["Textiles"]] unless csv_obj["Textiles"].nil?
        graph << [subject, RECYCLING_CENTRES.hasCans, csv_obj["Cans"]] unless csv_obj["Cans"].nil?
        graph << [subject, RECYCLING_CENTRES.hasFoil, csv_obj["Foil"]] unless csv_obj["Foil"].nil?
        graph << [subject, RECYCLING_CENTRES.hasPlasticBottles, csv_obj["Plastic Bottles"]] unless csv_obj["Plastic Bottles"].nil?
        graph << [subject, RECYCLING_CENTRES.hasAerosols, csv_obj["Aerosols"]] unless csv_obj["Aerosols"].nil?
        """