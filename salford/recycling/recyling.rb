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
RECYCLING_CENTRES = RDF::Vocabulary.new("http://data.gmdsp.org.uk/id/" + COUNCIL + "/recycling-centres/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
  rs
end


CSV.foreach('RecyclingCentres.csv', { headers:true }) do |csv_obj|
  # create a unique name for this recycling centre
  subject = RECYCLING_CENTRES[idify(csv_obj["UPRN"])]
  # add the recycling centre label
  graph << [subject, RDFS.label, csv_obj["Location"]]
  # add the recycling centre type
  graph << [subject, RDF.type, RDF::URI("http://data.gmdsp.org.uk/def/recycling-centre")]
  # add the address location
  graph << [subject, VCARD.hasStreetAddress, csv_obj["Address"]]
  # location information
  graph << [subject, OS.northing, csv_obj["Northings"]]
  graph << [subject, OS.easting, csv_obj["Eastings"]]

  # recycling information
  # graph << [subject, RECYCLING_CENTRES.hasCardboard, csv_obj["Cardboard"]]
  # graph << [subject, RECYCLING_CENTRES.hasPaper, csv_obj["Paper"]]
  # graph << [subject, RECYCLING_CENTRES.hasCartons, csv_obj["Cartons"]]
  # graph << [subject, RECYCLING_CENTRES.hasShoes, csv_obj["Shoes"]]
  # graph << [subject, RECYCLING_CENTRES.hasGlass, csv_obj["Glass"]]
  # graph << [subject, RECYCLING_CENTRES.hasTextiles, csv_obj["Textiles"]]
  # graph << [subject, RECYCLING_CENTRES.hasCans, csv_obj["Cans"]]
  # graph << [subject, RECYCLING_CENTRES.hasFoil, csv_obj["Foil"]]
  # graph << [subject, RECYCLING_CENTRES.hasPlasticBottles, csv_obj["Plastic Bottles"]]
  # graph << [subject, RECYCLING_CENTRES.hasAerosols, csv_obj["Aerosols"]]

  puts graph
end


RDF::RDFXML::Writer.open("recyclingcentres.rdf") do |writer|
  writer << graph
end
