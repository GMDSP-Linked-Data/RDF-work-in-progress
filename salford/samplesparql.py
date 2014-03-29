"""
Below are some example queries from data.gmdsp.org.uk and their sparql endpoint
"""
__author__ = 'jond'

import logging

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF

from SPARQLWrapper import SPARQLWrapper, JSON

# set up the sparl endpoint
sparql =  SPARQLWrapper("http://data.gmdsp.org.uk/sparql")


def basic_query():
    """
    Sample query that returns the allotments triples for salford
    """

    # get all the allotment data
    sparql.setQuery("""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT *
    WHERE {
      GRAPH <http://data.gmdsp.org.uk/graph/salford/allotments> {
        ?s ?p ?o
      }
    }
    LIMIT 20
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print result


def allotment_labels_query():
    """
    Sample query that returns all the unique labels in the salford allotment graph
    """
    # lets get all the allotment labels
    sparql.setQuery("""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?o
    WHERE {
      GRAPH <http://data.gmdsp.org.uk/graph/salford/allotments> {
        ?s rdfs:label ?o.
        ?s rdf:type <http://data.gmdsp.org.uk/def/council/allotment/Allotment>
      }
    }
    LIMIT 20
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print result['o']['value']




if __name__ == "__main__":
    query_functions = [
        basic_query,
        allotment_labels_query,
    ]

    for q in query_functions:
        q()
        print "------------------"
