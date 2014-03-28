__author__ = 'jond'

import csv
import datetime

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

# Source conversion notes:
# Some clean up of weird characters needed to happen on the source data

PLANNING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/')
PLANNING_APPLICATION_STATUS_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/planning-application-status/')
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
        if row["APP TYPE DECODE"]:
            graph.add((pa, PLANNING_ONT['applicationType'], PLANNING_APPLICATION_STATUS_ONT[utils.idify(row["APP TYPE DECODE"])]))
        if row["APP TYPE"]:
            graph.add((pa, PLANNING_ONT['applicationTypeCode'], Literal(row["APP TYPE"])))
        if row["DEVELOPMENT TYPE DECODE"]:
            graph.add((pa, PLANNING_ONT['developmentType'], PLANNING_APPLICATION_STATUS_ONT[utils.idify(row["DEVELOPMENT TYPE DECODE"])]))
        if row["PROPOSAL"]:
            graph.add((pa, PLANNING_ONT['proposal'], Literal(clean_string(row["PROPOSAL"]))))
        if row["VALIDATION DATE"]:
            validation_date = datetime.datetime.strptime(
                row["VALIDATION DATE"].split(" ")[0],
                "%d/%m/%Y",
            )
            graph.add((pa, PLANNING_ONT['validatedDate'], Literal(validation_date)))
        if row["RECOMMENDATION DECODE"]:
            graph.add((pa, PLANNING_ONT['decision'], PLANNING_APPLICATION_STATUS_ONT[utils.idify(row["RECOMMENDATION DECODE"])]))
        if row["DECISION DATE"]:
            decision_date = datetime.datetime.strptime(
                row["DECISION DATE"].split(" ")[0],
                "%d/%m/%Y",
            )
            graph.add((pa, PLANNING_ONT['decisionDate'], Literal(decision_date)))

        # planning application site
        pa_site = PLANNING["site/" + utils.idify(row["REFERENCE"])]
        graph.add((pa, PLANNING_ONT['planningApplicationSite'], pa_site))
        graph.add((pa_site, utils.RDFS['label'], Literal("Planning application site for planning application " + row["REFERENCE"])))
        graph.add((pa_site, utils.OS["northing"], Literal(row["NORTHING"])))
        graph.add((pa_site, utils.OS["easting"], Literal(row["EASTING"])))
        graph.add((pa_site, utils.VCARD['street-address'], Literal(clean_string(row["LOCATION"]))))




