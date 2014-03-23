__author__ = 'jond'

import json
import os
from xml.etree import ElementTree as ET

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

GRITTING = Namespace('http://data.gmdsp.org.uk/id/salford/gritting/')
GRITTING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/gritting/')

def convert(graph, input_path):
    i = 1
    for event, n in ET.iterparse(input_path, events=("end",)):
        if n.tag == "{http://www.opengis.net/kml/2.2}coordinates":
            gr = GRITTING["route{}".format(i)]
            graph.add((gr, RDF.type, GRITTING_ONT["GrittingRoute"]))
            graph.add((gr, utils.RDFS['label'], Literal("Gritting route {}".format(i))))

            # now create the geojson file
            route = {
                "type": "LineString",
                "coordinates": [],
            }

            coordlist = n.text.split(" ")
            for coord in coordlist:
                lat, lon, height = coord.split(',')
                route["coordinates"].append([float(lat), float(lon)])

            # so we need now to create the json file and write it
            with open(os.path.join("output", "route{}.json".format(i)), "w") as f:
                f.write(json.dumps(route))

            graph.add((
                gr,
                GRITTING_ONT["routeFile"],
                URIRef("https://raw.githubusercontent.com/GMDSP-Linked-Data/RDF-work-in-progress/master/finalised-output/salford/grittingroutes/route{}.json".format(i))))

            i = i+1





