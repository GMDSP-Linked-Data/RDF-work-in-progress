"""
Command line module for access to GMDSP converters

This will convert the specified input to an xml file in RDF format

General specification is:

>>> python main.py converter -i input -o output

Where converter is one of the following supported converters:
- allotments
- gritting
- parking
- planning
- recycling
- streetlight

For example:

>>> python main.py allotments -i ./sourcedata/allotments/allotments.csv -o ./output/allotments.rdf

"""

__author__ = 'jond'


def main():
    pass

if __name__ == "__main__":
    main()
