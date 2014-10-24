import os
import xml.etree.ElementTree as ET

from rdflib import Graph, URIRef, Namespace, RDF, Literal
from rdflib.store import VALID_STORE


storefn = "C:/Users/Matt/Desktop/RDF-work-in-progress/stockport/Output/parking.rdf"
storeuri = 'file://' + storefn

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
SCHEMA = Namespace('http://schema.org/')
SPACIAL = Namespace('http://data.ordnancesurvey.co.uk/ontology/spatialrelations/')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')

PARKING = Namespace('http://data.gmdsp.org.uk/id/manchester/parking/')
PARKING_ONT = Namespace('http://data.gmdsp.org.uk/def/manchester/parking/')

class Store:
    def __init__(self):
        self.graph = Graph(identifier=URIRef('http://www.google.com'))
        rt = self.graph.open(storeuri, create=False)
        if rt == None:
            self.graph.open(storeuri, create=True)
        else:
            assert rt == VALID_STORE, "The underlying store is corrupt"

        self.graph.bind("os", OS)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("geo", GEO)
        self.graph.bind("schema", SCHEMA)
        self.graph.bind("spacial", SPACIAL)

    def newCarPark(self, name, label, spaces, lat, long, address, postcode):
        carpark = PARKING[name]
        self.graph.add((carpark, RDF.type, PARKING_ONT["ParkingSite"]))
        self.graph.add((carpark, RDFS["label"], Literal(label + " car park")))

        self.graph.add((carpark, PARKING_ONT["totalNumberOfSpaces"], Literal(spaces)))

        self.graph.add((carpark, GEO["lat"], Literal(lat)))
        self.graph.add((carpark, GEO["long"], Literal(long)))

        self.graph.add((carpark, VCARD['hasAddress'], URIRef("http://data.gmdsp.org.uk/def/council/parking/address/" + name)))
        vcard = PARKING["address/" + name]
        self.graph.add((vcard, RDF.type, VCARD["Location"]))
        self.graph.add((vcard, RDFS['label'], Literal(label)))
        self.graph.add((vcard, VCARD['street-address'], Literal(address)))
        self.graph.add((vcard, VCARD['postal-code'], Literal(postcode)))


    def save(self):
        print storeuri
        self.graph.serialize(storefn, format="pretty-xml")

def main(argv=None):
    s = Store()
    tree = ET.parse("./Data/CarParks.xml")
    root = tree.getroot()
    carparks = tree.findall(".//fme:CarParks", namespaces={"fme": "http://www.safe.com/xml/xmltables"})
    for carpark in carparks:
        label = carpark.find("fme:name", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        name = label.replace(" ", "_").replace(",", "")
        address = label
        try:
            spaces = int(carpark.find("fme:totalcapacity", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text)
        except ValueError:
            spaces = 0
        lat = carpark.find("fme:lat", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        long = carpark.find("fme:long", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        postcode = carpark.find("fme:postcode", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        s.newCarPark(name, label, spaces, lat, long, address, postcode)

    print "saving"
    s.save()
    print "saved!"

if __name__ == '__main__':
    main()