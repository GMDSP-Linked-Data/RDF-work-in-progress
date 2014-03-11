
Notes
------------------
11 March 2014

On data

- I've transformed six datasets into RDF - all at: https://github.com/GMDSP-Linked-Data/RDF-work-in-progress/tree/master/trafford/RDF

- I've added these to the GMDSP platform: http://gmdsp-staging.publishmydata.com/data (guest:gmdsp99)

- The one remaining dataset is the gritting routes - as discussed it might be useful to look at alternatives to KML, but I have also raised this with other fellows

- I havent added all recycling types in just yet - as I may need to remodel that 

- Street lighting and Council tax banding are only small samples of the total dataset, to enable easy conversion, load and testing

- For geography, I've only utilised lat/long for now - need to clarify whether (and how) we lookup administrative geographies via this (see: https://github.com/GMDSP-Linked-Data/RDF-work-in-progress/issues/7)

On data modelling

- In most cases, the ontology for the various services/subjects has not been added to the platform.  When added, this enables you to see that allotments (for example) are part of the Allotment ontology, and access that - rather than just a URI.

- Some of the RDF has a mix of the "definition" of the data - reference to ESD standards *and* the data - aiming to resolve if this is necessary, or covered via ontologies (most likely)

- at present, I've tried to model the datasets in a consistent way.  I envisage changes via more iterations and liaison with other fellows.  By no means should the RDF present today be read as final or comprehensive!
