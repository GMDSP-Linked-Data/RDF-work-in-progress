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

import argparse
import importlib
from gmdspconverters import utils

parser = argparse.ArgumentParser(description="Command line module for access to the GMDSP converters.")
parser.add_argument(
    'converter',
    choices=[
        'allotments', 'gritting', 'parking', 'planning', 'recycling', 'streetlight',
    ],
    help="The converter to use"
)
parser.add_argument("-i", type=str, required=True, help="The input file.")
parser.add_argument("-o", type=str, required=True, help="The output file.")

args = parser.parse_args()


MODULE_MAP = {
    'allotments': 'allotments',
    'gritting': 'gritting',
    'parking': 'parking',
    'planning': 'planning',
    'recycling': 'recycling',
    'streetlight': 'streetlighting',
}

def main(convertertype, inputfile_path, outputfile_path):
    m = importlib.import_module('gmdspconverters.' + MODULE_MAP[convertertype])
    g = utils.create_graph()
    m.convert(g, inputfile_path)
    utils.output_graph(g, outputfile_path)


if __name__ == "__main__":
    main(args.converter, args.i, args.o)
