__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

# Source conversion notes:
# Some clean up of weird characters needed to happen on the source data

PLANNING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/')
PLANNING = Namespace('http://data.gmdsp.org.uk/id/salford/planning/')

def clean_string(s):
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.replace("", "")
    s = s.lstrip()
    s = s.rstrip()
    return s

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
    for row in reader:
        pa = PLANNING[utils.idify(row["REFERENCE"])]
        graph.add((pa, RDF.type, PLANNING_ONT["PlanningApplication"]))
        graph.add((pa, utils.RDFS['label'], Literal("Planning application " + row["REFERENCE"])))

        # planning application specific stuff
        graph.add((pa, PLANNING_ONT['applicationType'], Literal(row["APP TYPE DECODE"])))
        graph.add((pa, PLANNING_ONT['applicationTypeCode'], Literal(row["APP TYPE"])))
        graph.add((pa, PLANNING_ONT['developmentType'], Literal(row["DEVELOPMENT TYPE DECODE"])))
        graph.add((pa, PLANNING_ONT['proposal'], Literal(clean_string(row["PROPOSAL"]))))
        graph.add((pa, PLANNING_ONT['validatedDate'], Literal(row["VALIDATION DATE"])))
        graph.add((pa, PLANNING_ONT['decision'], Literal(row["RECOMMENDATION DECODE"])))
        graph.add((pa, PLANNING_ONT['decisionDate'], Literal(row["DECISION DATE"])))

        # planning application site
        pa_site = PLANNING["site/" + utils.idify(row["REFERENCE"])]
        graph.add((pa, PLANNING_ONT['planningApplicationSite'], pa_site))
        graph.add((pa_site, utils.RDFS['label'], Literal("Planning application site for planning application " + row["REFERENCE"])))
        graph.add((pa_site, utils.OS["northing"], Literal(row["NORTHING"])))
        graph.add((pa_site, utils.OS["easting"], Literal(row["EASTING"])))
        graph.add((pa_site, utils.VCARD['street-address'], Literal(clean_string(row["LOCATION"]))))




