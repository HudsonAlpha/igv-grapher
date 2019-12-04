#!/usr/bin/env python
from __future__ import print_function
import argparse
import gzip
import sys
import subprocess
import re

parser = argparse.ArgumentParser(description="Use IGV to graph BED regions")
parser.add_argument('-r', '--bed', type=str, help="BED input filename", required=True)
parser.add_argument('-t', '--title', type=int, help="BED title column", default=4)
parser.add_argument('-b', '--bams', type=str, help="BAMS", nargs='+', required=True)
parser.add_argument('-g', '--genome', type=str, default="hg38", help="Genome (hg19 or hg38)")
parser.add_argument('-p', '--prefix', type=str, default="", help="File prefix.")
parser.add_argument('-s', '--slop', type=int, default=0, help="Slop: Number of bases to add at beginning and end of graph")
parser.add_argument('-n', '--indel-bp-threshold', default=1, help="Hide indels below this length.")
parser.add_argument('--print', action="store_true", help="Print commands instead of executing them")
parser.add_argument('--bsub',action='store_true', help="use bsub.")

args = parser.parse_args()


if args.bed.endswith('gz'):
    inputfile = gzip.open(args.bed, 'rt')
else:
    inputfile = open(args.bed, 'r')

for line in inputfile:
    if line.startswith('#'):
        continue
    line = line.strip().split('\t')
    if len(line) == 1: # handle bed files that might be space-delimited
        line = line.strip().split(' ')
        if len(line) == 1:
            print('BED format error. {}'.format(line))
            inputfile.close()
            sys.exit()
    chrom = line[0]
    start = int(line[1])
    end = int(line[2])
    try:
        name = re.sub(r"[:,. \*]", "_", line[args.title - 1]) # clean to prevent filename weirdness
    except IndexError:
        print("Invalid column selected with -t.")
        inputfile.close()
        sys.exit()

    filename = "_".join([chrom,str(start),str(end)])
    if name != "":
        filename = filename + "_" + name
    if args.prefix != "":
        filename = args.prefix + "_" + filename
    width = abs(end-start)
    if args.slop == 0:
        slop = int(float(width)*0.10)
    else:
        slop = args.slop


    start = max(start - slop, 1)
    end = end + slop

    command = "/gpfs/gpfs2/cooperlab/igv-grapher/graph_region.sh -g {genome} -c {chrom} -s {start} -e {end} -n {threshold} -o {output}".format(genome=args.genome, start=start, end=end, chrom=chrom, threshold=args.indel_bp_threshold, output=filename+".png")
    for bam in args.bams:
        command += ' -b {}'.format(bam)
    if args.bsub:
        command = 'bsub -R rusage[mem=24576] -n 1 ' + command
    if args.print:
        print(command)
    else:
        command = command.split(' ')
        subprocess.call(command)



inputfile.close()
