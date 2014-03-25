__author__ = 'jond'

import os
import re

from rdflib import Graph, Namespace

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
ADMINGEO = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
SCHEME = Namespace('http://schema.org/')
QB = Namespace('http://purl.org/linked-data/cube#')

def idify(s):
    chars = [
        " ",
        ",",
        "/",
    ]
    s = re.sub('[%s]' % ''.join(chars), '-', s)
    return s.lower()

def create_graph():

    graph = Graph()
    graph.bind('os', OS)
    graph.bind('rdfs', RDFS)
    graph.bind('geo', GEO)
    graph.bind('vcard', VCARD)
    graph.bind('scheme', SCHEME)
    graph.bind('qb', QB)

    return graph

def output_graph(graph, output_path):
    storefn = os.path.realpath(output_path)
    storeuri = 'file://'+storefn
    graph.serialize(storeuri, format='pretty-xml')