#!/usr/bin/env python
from __future__ import print_function
import argparse
import gzip
import sys
import subprocess
import re

parser = argparse.ArgumentParser(description="Use IGV to graph BED regions")
parser.add_argument('-v', '--vcf', type=str, help="VCF input filename", required=True)
parser.add_argument('-b', '--bams', type=str, help="BAMS", nargs='+', required=True)
parser.add_argument('-g', '--genome', type=str, default="hg38", help="Genome (hg19 or hg38)")
parser.add_argument('-p', '--prefix', type=str, default="", help="File prefix.")
parser.add_argument('-s', '--slop', type=int, default=0, help="Slop: Number of bases to add at beginning and end of graph")
parser.add_argument('-n', '--indel-bp-threshold', default=1, help="Hide indels below this length.")
parser.add_argument('--print', action="store_true", help="Print commands instead of executing them")
parser.add_argument('--bsub', action="store_true", help="Submit via LSF to default queue with recommended resources.")


args = parser.parse_args()


if args.vcf.endswith('gz'):
    inputfile = gzip.open(args.vcf, 'rt')
else:
    inputfile = open(args.vcf, 'r')

for line in inputfile:
    if line.startswith('#'):
        continue
    line = line.strip().split('\t')
    if len(line) == 1:
        print('VCF format error. {}'.format(line))
        inputfile.close()
        sys.exit()
    chrom = line[0]
    pos = int(line[1])
    id = line[2]
    ref = line[3]
    alt = line[4]
    qual = line[5]
    filter = line[6]
    info = line[7]
    format = line[8]
    info_dict = {x.split('=')[0]: x.split('=')[1] for x in info.split(';') if '=' in x}
    #info_list = [x: True for x in info.split(';') if '=' not in x]
    start = pos
    if 'END' in info_dict:
        end = int(info_dict['END'])
    else:
        end = start + 30

    name = ""
    if id != '.':
        name = name + "_" + id
    if 'SVTYPE' in info_dict:
        name = name + "_" + info_dict['SVTYPE']
    if 'SVANN' in info_dict:
        name = name + "_" + info_dict['SVANN']

    name = re.sub(r"[:,. \*]", "_", name) # clean to prevent filename weirdness


    filename = "_".join([chrom,str(start),str(end)])
    if name != "":
        filename = filename + "_" + name
    if args.prefix != "":
        filename = args.prefix + "_" + filename
    if args.slop == 0:
        width = abs(end-start)
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
