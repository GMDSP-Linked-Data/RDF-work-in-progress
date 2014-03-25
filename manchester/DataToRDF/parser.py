__author__ = 'danielkershaw'
from rdflib import Graph

g = Graph()
data = open("Output/planning.rdf", "rb")
g.parse(data, format='application/rdf+xml')