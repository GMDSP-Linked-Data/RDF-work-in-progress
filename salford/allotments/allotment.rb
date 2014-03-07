require 'rdf'
require 'rdf/ntriples'
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

# our new vocabulary
ALLOTMENTS = RDF::Vocabulary.new("http://data.gmdsp.org.uk/" + COUNCIL + "/allotments/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
end


CSV.foreach('allotments.csv', { headers:true }) do |csv_obj|
  # create a unique name for this allotment
  label = csv_obj["Name"]
  subject = ALLOTMENTS[idify(label)]
  #latlong = a.elements.to_a('Point/coordinates')[0].text
  #subject = ALLOTMENTS[URI::encode(label)]

  # add the allotment label
  graph << [subject, RDFS.label, label]
  # add the allotment type
  #graph << [subject, RDF.type, RDF::Literal("Allotment")]
  # add the point location
  # graph << [subject, GEO.lat_long, RDF::Literal(latlong)]
end

File.write("allotments.rdf", graph.dump(:ntriples))

# dump the triples
puts
