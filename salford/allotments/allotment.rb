#!usr/bin/ruby

require 'rubygems'
gem 'rdf'
gem 'rdf-rdfxml'

require 'open-uri'
require 'csv'
require 'rdf'
require 'rdf/rdfxml'

COUNCIL = "salford"

# add the data to the graph
graph = RDF::Graph.new

# set up the vocabulary
RDFS = RDF::RDFS
GEO = RDF::GEO
VCARD = RDF::VCARD
OS = RDF::Vocabulary.new("http://data.ordnancesurvey.co.uk/ontology/spatialrelations/")

# our new vocabulary
ALLOTMENTS = RDF::Vocabulary.new("http://data.gmdsp.org.uk/id/" + COUNCIL + "/Allotment/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
end


CSV.foreach('allotments.csv', { headers:true }) do |csv_obj|
  # create a unique name for this allotment
  label = csv_obj["Name"]
  idify_label = idify(label)
  subject = ALLOTMENTS[idify_label]

  # add the allotment label
  graph << [subject, RDFS.label, label]
  # add the allotment type
  graph << [subject, RDF.type, RDF::URI("http://data.gmdsp.org.uk/def/council/allotment/")]
  # add the address location
  unless csv_obj["Address"].nil?
    vcard_subject = ALLOTMENTS["#{idify_label}/address"]
    graph << [subject, VCARD.hasAddress, vcard_subject]
    graph << [vcard_subject, RDF.type, VCARD.Location]
    graph << [vcard_subject, VCARD.hasStreetAddress, csv_obj["Address"]]
  end

  # location information
  graph << [subject, OS.northing, csv_obj["Northing"]]
  graph << [subject, OS.easting, csv_obj["Easting"]]


end


RDF::RDFXML::Writer.open("allotments.rdf") do |writer|
  writer << graph
end
