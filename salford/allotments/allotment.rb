require 'rdf'
require 'rdf/ntriples'
require 'rexml/document'
require 'open-uri'

include RDF

# parse the allotment data our the source file
xml = File.read('allotments.kml')

xmldoc = REXML::Document.new(xml)
allotments = []

xmldoc.elements.each('kml/Document/Placemark') do |p|
  allotments << p
end

# add the data to the graph
graph = RDF::Graph.new

# set up the vocabulary
RDFS = RDF::RDFS
GEO = RDF::GEO
VCARD = RDF::VCARD

# our new vocabulary
AL = RDF::Vocabulary.new("https://gmdsp-admin.publishmydata.com/id/Allotments/")

allotments.each do |a|
  # create a unique name for this allotment
  label = a.elements.to_a('name')[0].text
  latlong = a.elements.to_a('Point/coordinates')[0].text
  subject = AL[URI::encode(label)]

  # add the allotment label
  graph << [subject, RDFS.label, label]
  # add the allotment type
  graph << [subject, RDF.type, RDF::Literal("Allotment")]
  # add the point location
  graph << [subject, GEO.lat_long, RDF::Literal(latlong)]
end

# dump the triples
puts graph.dump(:ntriples)
