require 'rdf'
require 'rdf/rdfxml'
require 'open-uri'
require 'csv'

include RDF

COUNCIL = "salford"


# set up the vocabulary
RDFS = RDF::RDFS
GEO = RDF::GEO
VCARD = RDF::VCARD
OS = RDF::Vocabulary.new("http://data.ordnancesurvey.co.uk/ontology/admingeo/")

# our new vocabulary
PLANNING = RDF::Vocabulary.new("http://data.gmdsp.org.uk/id/" + COUNCIL + "/planning-application/")

def idify(s)
  rs = s.downcase
  rs.gsub!(" ", "-")
  rs.gsub!("/", "-")
  rs
end

# add the data to the graph
graph = RDF::Graph.new

read_files = [
    'planning-applications.csv',
    'planning-applications-2.csv'
]

for read_file_name in read_files
  # the planning application file may need some massaging
  read_file = File.open(read_file_name, 'r')
  write_file = File.open('planning-applications-clean.csv', 'w+')

  total_quotes = 0
  line_number = 0
  line_string = ""
  read_file.each_char { |c|
    line_string += c
    if c == "\""
      total_quotes += 1
    end
    if c == "\n"
      line_number += 1
      # puts "Line Number: #{line_number} Line string: '#{line_string}' Quotes: #{total_quotes}"
      # skip if we have a crazy number of quotes
      next if total_quotes % 2 == 1
      # else write the line to the file

      # and reset our flags
      total_quotes = 0
      line_string = ""
    end
    write_file.write(c)
  }

  read_file.close
  write_file.close
end

CSV.foreach('planning-applications-clean.csv', { headers:true }) do |csv_obj|
  # add the data to the graph
  # This is useful for debugging
  # graph = RDF::Graph.new
  # "REFERENCE","LOCATION","APP TYPE","APP TYPE DECODE","VALIDATION DATE","PROPOSAL","RECOMMENDATION","RECOMMENDATION DECODE","DECISION DATE","DEVELOPMENT TYPE","DEVELOPMENT TYPE DECODE","WARD","WARD DECODE","NORTHING","EASTING","KEY VALUE"
  label = csv_obj["REFERENCE"]
  idify_label = idify(label)
  # create a unique name for this application
  subject = PLANNING[idify_label]
  # add the label
  graph << [subject, RDFS.label, label]
  # add the  type
  graph << [subject, RDF.type, RDF::URI("http://data.gmdsp.org.uk/def/planning-application")]
  # add the address location
  if csv_obj["LOCATION"] != NIL
    graph << [subject, VCARD.hasStreetAddress, csv_obj["LOCATION"]]
  end
  # location information
  graph << [subject, OS.northing, csv_obj["NORTHING"]]
  graph << [subject, OS.easting, csv_obj["EASTING"]]

  # planning specific information
  graph << [subject, PLANNING.applicationTypeShort, csv_obj["APP TYPE"]]
  graph << [subject, PLANNING.applicationType, csv_obj["APP TYPE DECODE"]]
  graph << [subject, PLANNING.validationDate, csv_obj["VALIDATION DATE"]]
  graph << [subject, PLANNING.proposal, csv_obj["PROPOSAL"]]
  graph << [subject, PLANNING.recommendationShort, csv_obj["RECOMMENDATION"]]
  graph << [subject, PLANNING.recommendation, csv_obj["RECOMMENDATION DECODE"]]
  graph << [subject, PLANNING.decisionDate, csv_obj["DECISION DATE"]]
  graph << [subject, PLANNING.developmentTypeShort, csv_obj["DEVELOPMENT TYPE"]]
  graph << [subject, PLANNING.developmentTypeShort, csv_obj["DEVELOPMENT TYPE DECODE"]]
  graph << [subject, PLANNING.wardShort, csv_obj["WARD"]]
  graph << [subject, PLANNING.ward, csv_obj["WARD DECODE"]]
  graph << [subject, PLANNING.keyValue, csv_obj["KEY VALUE"]]

  # This section is helpful for debugging
  #begin
  #  RDF::RDFXML::Writer.open("planning-applications-#{idify_label}.rdf") do |writer|
  #    writer << graph
  #  end
  #rescue RDF::WriterError => e
  #  puts "failed to write planning-applications-#{idify_label}.rdf"
  #end
end

puts "This takes a while..."

RDF::RDFXML::Writer.open("planning-applications.rdf") do |writer|
  writer << graph
end

