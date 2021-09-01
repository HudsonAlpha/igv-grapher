#!/usr/bin/env /cluster/home/jlawlor/envs/igvgraph/bin/python3.9
from __future__ import print_function
import argparse
import img2pdf

parser = argparse.ArgumentParser(description="Combine image files into a png.")
parser.add_argument('-o', '--output', type=str, required=True, help="File prefix.")
parser.add_argument('imagefiles', type=str, nargs="*", help="image files to combine into pdf")
args = parser.parse_args()
print('Combining {} to {}'.format(" ".join(args.imagefiles), args.output))
with open(args.output, "wb") as pdf:
    pdf.write(img2pdf.convert(args.imagefiles))
print('Done')
