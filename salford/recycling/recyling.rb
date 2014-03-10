require 'rdf'
require 'rdf/rdfxml'
require 'open-uri'
require 'csv'

include RDF

COUNCIL = "salford"

# add the data to the graph
graph = RDF::Graph.new

# set up the vocabulary
RDFS = RDF::RDFS
GEO = RDF::GEO
VCARD = RDF::VCARD
OS = RDF::Vocabulary.new("http://data.ordnancesurvey.co.uk/ontology/admingeo/")

# our new vocabulary
ALLOTMENTS = RDF::Vocabulary.new("http://data.gmdsp.org.uk/id/" + COUNCIL + "/recycling-centres/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
end


CSV.foreach('RecyclingCentres.csv', { headers:true }) do |csv_obj|
  # create a unique name for this allotment
  label = csv_obj["Name"]
  subject = ALLOTMENTS[idify(label)]

  # add the allotment label
  graph << [subject, RDFS.label, label]
  # add the allotment type
  graph << [subject, RDF.type, RDF::URI("http://data.gmdsp.org.uk/def/allotment")]
  # add the address location
  graph << [subject, VCARD.hasStreetAddress, csv_obj["Address"]]
  # location information
  graph << [subject, OS.northing, csv_obj["Northing"]]
  graph << [subject, OS.easting, csv_obj["Easting"]]

end


RDF::RDFXML::Writer.open("allotments.rdf") do |writer|
  writer << graph
end
