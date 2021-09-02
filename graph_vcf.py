#!/usr/bin/env /cluster/home/jlawlor/envs/igvgraph/bin/python3.9
from __future__ import print_function
import argparse
import gzip
import sys
import subprocess
import re
from pybedtools import BedTool
import tempfile
import os
import img2pdf
import tempfile
import time

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="Use IGV to graph BED regions")
parser.add_argument('-v', '--vcf', type=str, help="VCF input filename", required=True)
parser.add_argument('-b', '--bams', type=str, help="BAMS", nargs='+', required=True)
parser.add_argument('-g', '--genome', type=str, default="/cluster/lab/gcooper/igv-grapher/genomes/hg38/hg38.genome", help="Genome (hg19 or hg38)")
parser.add_argument('-p', '--prefix', type=str, default="", help="File prefix.")
parser.add_argument('-s', '--slop', type=int, default=0, help="Slop: Number of bases to add at beginning and end of full graph")
parser.add_argument('-k', '--breakpoint-slop', type=int, default=500, help="Number of bases to add at beginning and end of breakpoint graph")
parser.add_argument('-n', '--indel-bp-threshold', default=10, help="Hide indels below this length.")
parser.add_argument('-w', '--max-width', default=10, type=float, help="Largest width event to graph at once. (MB). Above this size will only graph breakpoints")
parser.add_argument('--print', action="store_true", help="Print commands instead of executing them")
parser.add_argument('--bsub', action="store_true", help="Submit via LSF to default queue with recommended resources.")
#parser.add_argument('-r', '--regions', type=str, help="Regions of interest. Only print events intersecting these items.")



args = parser.parse_args()

#if args.regions:
#    tmpvcf = tempfile.NamedTemporaryFile()
#    cmd = 'bcftools view -R {regionsfilename} -O v -o {vcf}'

if args.vcf.endswith('gz'):
    inputfile = gzip.open(args.vcf, 'rt')
else:
    inputfile = open(args.vcf, 'r')
variant_text = tempfile.mkstemp(suffix='.txt', dir='/scratch/lab/gcooper/')[1]
header = ""
for line in inputfile:
    if line.startswith('#'):
        if "CHROM" in line:
            header = line.replace("\t", " ")
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
    try:
        rest = str(line[8:])
    except IndexError:
        rest = ""
    #format = line[8]
    info_dict = {x.split('=')[0]: x.split('=')[1] for x in info.split(';') if '=' in x}
    #info_list = [x: True for x in info.split(';') if '=' not in x]
    # Get original start and end. Do this first so we have a trace in filename

    with open(variant_text, 'wt') as f:
        f.write("HEADER: {}\n\n\n".format(header))
        f.write("CHROM: {}\n\n\n".format(chrom))
        f.write("POS: {}\n\n\n".format(pos))
        f.write("ID: {}\n\n\n".format(id))
        f.write("REF: {}\n\n\n".format(ref))
        f.write("ALT: {}\n\n\n".format(alt))
        f.write("QUAL: {}\n\n\n".format(qual))
        f.write("FILTER: {}\n\n\n".format(filter))
        for x in info_dict:
            f.write("{}: {}\n\n\n".format(x, info_dict[x]))
        f.write("GENOTYPES: {}\n\n\n".format(rest))


    svlen = int(info_dict.get('SVLEN', 0))
    start = pos
    try:
        bnd_mate_chrom = re.compile('(chr.+)[\[\]]').search(alt).group(1).split(":")[0] #match everything from chr to right before a [ or ]. This excludes HLA* chromosomes but that's ok. Previously (chr[0-9XYM]+[:][0-9]+)
    except AttributeError:
        bnd_mate_chrom = None
    try:
        bnd_mate_pos = int(re.compile('(chr.+)[\[\]]').search(alt).group(1).split(":")[1])
    except AttributeError:
        bnd_mate_pos = None

    if info_dict.get('SVTYPE') == 'TRA':
        continue
    if 'END' in info_dict:
        end = int(info_dict['END'])
    else:
        end = start
    # Build filename
    name = ""
    svtype = None
    if id != '.':
        name = name + "_ID." + id
    if 'SVTYPE' in info_dict:
        name = name + "_TYPE." + info_dict['SVTYPE']
        svtype = info_dict['SVTYPE']
    if 'SVANN' in info_dict:
        name = name + "_ANN." + info_dict['SVANN']
    if 'SVLEN' in info_dict:
        name = name + "_LEN." + info_dict['SVLEN']


    name = re.sub(r"[:,. \*]", "_", name) # clean to prevent filename weirdness


    filename = "_".join([chrom,str(start),str(end)])
    if name != "":
        filename = filename + "_" + name
    if args.prefix != "":
        filename = args.prefix + "_" + filename

    # Modify start and end with slop
    width = abs(end-start)
    if args.slop == 0:
        if width > 1000000:
            expand = 0.10
        else:
            expand = 0.45
        slop = max(int(float(width)*expand),500)
    else:
        slop = args.slop

    #print("for main, calculated {} width, {} slop, {} start, {} end".format(width, slop, max(start - slop, 1), end + slop))

    command = ""


    temps_and_settings = []

    if svtype == 'BND':
        temps_and_settings.append(
            {
                'chrom': chrom,
                'start': start - args.breakpoint_slop,
                'end': start + args.breakpoint_slop,
                'name': tempfile.mkstemp(suffix='.png', dir='/scratch/lab/gcooper/')[1],
                'indel': 1

            }
        )
        # mate breakpoint
        temps_and_settings.append(
            {
                'chrom': bnd_mate_chrom,
                'start': bnd_mate_pos - args.breakpoint_slop,
                'end': bnd_mate_pos + args.breakpoint_slop,
                'name': tempfile.mkstemp(suffix='.png', dir='/scratch/lab/gcooper/')[1],
                'indel': 1

            }
        )

    else:
        # Typical settings for the main graph
        if width <= args.max_width*1000000:
            temps_and_settings.append(
                {
                    'chrom': chrom,
                    'start': max(start - slop, 1),
                    'end': end + slop,
                    'name': tempfile.mkstemp(suffix='.png', dir='/scratch/lab/gcooper/')[1],
                    'indel': args.indel_bp_threshold

                }
            )

        if width > 1000: # If wider than a comfortable view, we will print each endpoint as well
            # left breakpoint
            temps_and_settings.append(
                {
                    'chrom': chrom,
                    'start': start - args.breakpoint_slop,
                    'end': start + args.breakpoint_slop,
                    'name': tempfile.mkstemp(suffix='.png', dir='/scratch/lab/gcooper/')[1],
                    'indel': 1

                }
            )
            # right breakpoint
            temps_and_settings.append(
                {
                    'chrom': chrom,
                    'start': end - args.breakpoint_slop,
                    'end': end + args.breakpoint_slop,
                    'name': tempfile.mkstemp(suffix='.png', dir='/scratch/lab/gcooper/')[1],
                    'indel': 1

                }
            )

    temps = [ x['name'] for x in temps_and_settings ]
    #print(temps_and_settings)
    for graph in temps_and_settings:
        #print((start,end,name,args.slop))
        command += "{SCRIPT_PATH}/graph_region.sh -g {genome} -c {chrom} -s {start} -e {end} -n {threshold} -o {output}".format(SCRIPT_PATH=SCRIPT_PATH, genome=args.genome, start=graph['start'], end=graph['end'], chrom=graph['chrom'], threshold=graph['indel'], output=graph['name'])
        for bam in args.bams:
            command += ' -b {}'.format(bam)
        command += ' && '

    command += "/cluster/software/imagemagick-7.0.7/bin/mogrify -background white -alpha remove -alpha off " + " ".join(temps)
    command += ' && '
    command += SCRIPT_PATH + "/make_pdf.py --textfile " + variant_text + " -o " + filename + ".pdf " + " ".join(temps)
    #with open(filename + ".pdf", "wb") as pdf:
    #    pdf.write(img2pdf.convert(['all.png', 'left.png', 'right.png']))

    if args.print:
        print(command)
    else:

        if args.bsub:
            command = 'bsub -R rusage[mem=24576] -n 1 -o igv_grapher.log ' + '"' + command + '"'
        print("graphing {}".format(filename))
        #time.sleep(1)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("Captured error")
            print("****stdout****")
            print(result.stdout)
            print("****stderr****")
            print(result.stderr)
            #sys.exit()
        if args.bsub:
            print(result.stdout)
            print(result.stderr)


# We ought to clean up the tempfiles that we've dumped into scratch, however if we're printing or bsubbing, this function exits before we're done with them

inputfile.close()
