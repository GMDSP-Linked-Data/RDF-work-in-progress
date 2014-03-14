require 'rdf'
require 'rdf/rdfxml'
require 'open-uri'
require 'csv'
require './osgbconvert'

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
PARKING = RDF::Vocabulary.new("http://data.gmdsp.org.uk/id/" + COUNCIL + "/parking/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
  rs
end


CSV.foreach('CarParks.csv', { headers:true }) do |csv_obj|
  label = csv_obj["Name"]
  # create a unique name
  subject = PARKING[idify(label)]
  # add the label
  graph << [subject, RDFS.label, label]
  # add the recycling centre type
  graph << [subject, RDF.type, RDF::URI("http://data.gmdsp.org.uk/def/parking")]
  # add the address location
  graph << [subject, VCARD.hasStreetAddress, csv_obj["Address"]]
  # location information
  osgb36point = convertWGS84toOSGB36(csv_obj["Latitude"].to_f, csv_obj["Longitude"].to_f, 0)
  locations = LatLongToOSGrid(osgb36point[0], osgb36point[1])
  graph << [subject, OS.easting, locations[0]]
  graph << [subject, OS.northing, locations[1]]

  # parking type
  graph << [subject, PARKING.type, csv_obj["Type"]] unless csv_obj["Type"].nil?

  # Operator info - should this be a organisation type?
  graph << [subject, PARKING.operator, csv_obj["Operator"]] unless csv_obj["Operator"].nil?
  graph << [subject, PARKING.operatorUrl, csv_obj["URL"]] unless csv_obj["URL"].nil?


end


RDF::RDFXML::Writer.open("carparks.rdf") do |writer|
  writer << graph
end
