import time
import xml.etree.ElementTree as ET

from rdflib import Graph, URIRef, Namespace, RDF, Literal
from rdflib.store import VALID_STORE

datafile = "./Data/planning.xml"

storefn = "./Output/planning.rdf"
storeuri = 'file://' + storefn

OS = Namespace('http://data.ordnancesurvey.co.uk/ontology/admingeo/')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
DECISION = Namespace('http://purl.org/cerif/frapo/')

PLANNING = Namespace('http://data.gmdsp.org.uk/def/council/planning/')
PLANNINGID = Namespace('http://data.gmdsp.org.uk/id/stockport/planning/')


class Store:
    def __init__(self):
        self.graph = Graph(identifier=URIRef('http://www.google.com'))
        self.refs = [];
        self.decisions = []
        self.types = []
        rt = self.graph.open(storeuri, create=False)
        if rt == None:
            self.graph.open(storeuri, create=True)
        else:
            assert rt == VALID_STORE, "The underlying store is corrupt"

        self.graph.bind("os", OS)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("geo", GEO)
        self.graph.bind('vcard', VCARD)
        self.graph.bind("planning", PLANNING)
        self.graph.bind('id', PLANNINGID)
        self.graph.bind('decision', DECISION)

    def newApplication(self, ref, address, recdate, decision, dcndate, lat, long, type, details):

        ref = ref.replace("/", "-").lower()
        mod = 0;
        if ref in self.refs:
            oref = ref
            while ref in self.refs:
                mod += 1
                ref = oref + "-" + `mod`

        self.refs.append(ref)

        if type not in self.types:
            self.new_type(type)
            self.types.append(type)

        app = PLANNINGID[ref]
        self.graph.add((app, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/planning/PlanningApplication')))
        self.graph.add((app, VCARD['street-address'], Literal(address)))
        self.graph.add((app, GEO["lat"], Literal(lat)))
        self.graph.add((app, GEO["long"], Literal(long)))
        self.graph.add((app, PLANNING['applicationType'], URIRef(
            'http://data.gmdsp.org.uk/def/council/planning/planning-application-type/' + type.replace(" ",
                                                                                                      "-").lower())))

        if details != None:
            self.graph.add((app, PLANNING["proposal"], Literal(details)))

        if decision != None:
            if decision not in self.decisions:
                self.new_decision(decision)
                self.decisions.append(decision)
            self.graph.add((app, PLANNING['decision'], URIRef(
                'http://data.gmdsp.org.uk/def/council/planning/planning-application-status/' + decision.replace(" ",
                                                                                                                "-").lower())))

        if recdate != None:
            self.graph.add((app, PLANNING['validatedDate'], URIRef('http://reference.data.gov.uk/id/day/' + time.strftime('%Y-%m-%d', recdate))))

        if dcndate != None:
            self.graph.add((app, PLANNING['validatedDate'], URIRef('http://reference.data.gov.uk/id/day/' + time.strftime('%Y-%m-%d', dcndate))))


    def save(self):
        print "saving to \"" + storefn +"\"..."
        self.graph.serialize(storefn, format="pretty-xml")

    def new_decision(self, decision):
        decision = PLANNINGID[decision.replace(" ", "-").lower()]
        self.graph.add((decision, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/planning/decision')))
        self.graph.add((decision, RDFS["label"], Literal(decision)))

    def new_type(self, type):
        type = PLANNINGID[type.replace(" ", "-").lower()]
        self.graph.add(
            (type, RDF.type, URIRef('http://data.gmdsp.org.uk/def/council/neighbourhood/planning/application-type')))
        self.graph.add((type, RDFS["label"], Literal(type)))


def main(argv=None):
    s = Store()
    tree = ET.parse(datafile)
    root = tree.getroot()
    applications = tree.findall(".//fme:PlanningApplicationsLast3years",
                                namespaces={"fme": "http://www.safe.com/xml/xmltables"})
    print "parsing \"" + datafile + "\"..."
    for application in applications:
        ref = application.find("fme:CaseFullRef", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        type = application.find("fme:AppType", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        try:
            details = application.find("fme:Proposal", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        except AttributeError:
            details = None
        address = application.find("fme:LocAddress1", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        try:
            recdate = time.strptime(application.find("fme:RecDate", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text, "%d/%m/%Y %H:%M:%S")
        except AttributeError:
            recdate = None
        try:
            dcndate = time.strptime(application.find("fme:DcnDate", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text, "%d/%m/%Y")
        except AttributeError:
            dcndate = None
        try:
            decision = application.find("fme:finaldecision", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        except AttributeError:
            decision = None
        long = application.find("fme:long", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text
        lat = application.find("fme:lat", namespaces={"fme": "http://www.safe.com/xml/xmltables"}).text

        s.newApplication(ref, address, recdate, decision, dcndate, lat, long, type, details)

    s.save()


if __name__ == '__main__':
    main()