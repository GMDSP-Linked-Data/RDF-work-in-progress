__author__ = 'jond'

import os

from rdflib import Graph, Namespace
from rdflib.store import VALID_STORE

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
POST = Namespace('http://data.ordnancesurvey.co.uk/ontology/postcode/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
SCHEME = Namespace('http://schema.org/')
QB = Namespace('http://purl.org/linked-data/cube#')

def idify(s):
    return s.replace(" ", "-").replace(",","-").lower()

def create_graph(output_path):

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