__author__ = 'jond'

import os
import re

from rdflib import Graph, Namespace
from pyproj import Proj, transform

v84 = Proj(proj="latlong",towgs84="0,0,0",ellps="WGS84")
v36 = Proj(proj="latlong", k=0.9996012717, ellps="airy",
        towgs84="446.448,-125.157,542.060,0.1502,0.2470,0.8421,-20.4894")
vgrid = Proj(init="world:bng")

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
    s = s.lstrip()
    s = s.rstrip()
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

def convertpostcodeto_osuri(postcode):
    os_postcode = postcode.replace(" ", "").upper()
    return "http://data.ordnancesurvey.co.uk/id/postcodeunit/"+os_postcode


def ENtoLL84(easting, northing):
    """Returns (longitude, latitude) tuple
    """
    vlon36, vlat36 = vgrid(easting, northing, inverse=True)
    return transform(v36, v84, vlon36, vlat36)

def LL84toEN(longitude, latitude):
    """Returns (easting, northing) tuple
    """
    vlon36, vlat36 = transform(v84, v36, longitude, latitude)
    return vgrid(vlon36, vlat36)