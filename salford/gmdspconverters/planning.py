__author__ = 'jond'

import csv
import datetime
import json
import urllib2
import decimal

from rdflib import URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD

from gmdspconverters import utils

# Source conversion notes:
# Some clean up of weird characters needed to happen on the source data

PLANNING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/')
PLANNING_APPLICATION_STATUS_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/planning-application-status/')
PLANNING_APPLICATION_TYPE_ONT = Namespace('http://data.gmdsp.org.uk/def/council/planning/planning-application-type/')
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
    non_existent_uris = set()
    rows = list(reader)
    row_length = len(rows)
    for index, row in enumerate(rows):
        # this takes a while so lets provide some context
        print "{}/{}".format(index, row_length)
        pa = PLANNING[utils.idify(row["REFERENCE"])]
        graph.add((pa, RDF.type, PLANNING_ONT["PlanningApplication"]))
        graph.add((pa, utils.RDFS['label'], Literal("Planning application " + row["REFERENCE"])))

        # planning application specific stuff
        if row["APP TYPE DECODE"]:
            graph.add((pa, PLANNING_ONT['applicationType'], PLANNING_APPLICATION_STATUS_ONT[utils.idify(row["APP TYPE DECODE"])]))
        if row["APP TYPE"]:
            graph.add((pa, PLANNING_ONT['applicationTypeCode'], Literal(row["APP TYPE"])))
        if row["DEVELOPMENT TYPE DECODE"]:
            graph.add((pa, PLANNING_ONT['developmentType'], PLANNING_APPLICATION_TYPE_ONT[utils.idify(row["DEVELOPMENT TYPE DECODE"])]))
        if row["PROPOSAL"]:
            graph.add((pa, PLANNING_ONT['proposal'], Literal(clean_string(row["PROPOSAL"]))))
        if row["VALIDATION DATE"]:
            validation_date = datetime.datetime.strptime(
                row["VALIDATION DATE"].split(" ")[0],
                "%d/%m/%Y",
            )
            try:
                date_string = validation_date.strftime("%Y-%m-%d")
                graph.add((pa, PLANNING_ONT['validatedDate'], utils.DATE[date_string]))
            except ValueError:
                # This means we were unable to parse a valid date
                # so just don't ' this node to the graph
                pass

        if row["RECOMMENDATION DECODE"]:
            graph.add((pa, PLANNING_ONT['decision'], PLANNING_APPLICATION_STATUS_ONT[utils.idify(row["RECOMMENDATION DECODE"])]))
        if row["DATEDECISS"]:
            decision_date = datetime.datetime.strptime(
                row["DATEDECISS"].split(" ")[0],
                "%d/%m/%Y",
            )
            try:
                date_string = decision_date.strftime("%Y-%m-%d")
                graph.add((pa, PLANNING_ONT['decisionDate'], utils.DATE[date_string]))
            except ValueError:
                # This means we were unable to parse a valid date
                # so just don't ' this node to the graph
                pass

        # planning application site
        pa_site = PLANNING["site/" + utils.idify(row["REFERENCE"])]
        graph.add((pa, utils.VCARD['hasAddress'], pa_site))
        graph.add((pa_site, RDF.type, PLANNING_ONT['PlanningApplicationSite']))
        graph.add((pa_site, utils.RDFS['label'], Literal("Planning application site for planning application " + row["REFERENCE"])))

        # postcode helper used here to remove the postcode if we find it
        street_address, address_postcode = utils.postcode_helper(clean_string(row["LOCATION"]))
        graph.add((pa_site, utils.VCARD['street-address'], Literal(street_address)))
        graph.add((pa_site, utils.VCARD['postal-code'], Literal(row["Postcode"])))
        os_postcodeuri = utils.convertpostcodeto_osuri(row["Postcode"])
        graph.add((pa_site, utils.POST['postcode'], URIRef(os_postcodeuri)))

        # so now we are going to generate lat/long information based on the postcode centroids
        try:
            os_postcodedata = json.load(urllib2.urlopen(os_postcodeuri + ".json"))
            graph.add((pa_site, utils.GEO["lat"], Literal(float(os_postcodedata[os_postcodeuri][str(utils.GEO["lat"])][0]["value"]))))
            graph.add((pa_site, utils.GEO["long"], Literal(float(os_postcodedata[os_postcodeuri][str(utils.GEO["long"])][0]["value"]))))
        except urllib2.HTTPError:
            # print "Unable to load data from: ", os_postcodeuri
            non_existent_uris.add(os_postcodeuri)
            pass

    print "Unable to locate the following uri's:", non_existent_uris









