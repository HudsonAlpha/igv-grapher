# igv-grapher
This is a tool used internally at the HudsonAlpha Institute for Biotechnology and is presented for the purposes of publication. It has not been designed to be portable outside of the HudsonAlpha compute cluster, so use elsewhere will require customization.

## Overview
Given a BED file and either a bed file of genomic regions or VCF of structural variant calls, use IGV in headless mode to make graphs.

Cluster location: `/cluster/lab/gcooper/igv-grapher`

Given coordinates and BAM / BED / GFF and other IGV-viewable files, `graph_region.sh` calls IGV and saves a jpg image in the current working directory.
`graph_bed.py` loops through a BED file and for each interval saves a jpg image in the current working directory.
`graph_vcf.py` loops through a VCF and for each variant entry saves a pdf image with a (1) graph of the entire variant, (2) for variants > 1kb, graphs of each endpoint, and (3) information from the VCF record (ex: genotypes, INFO field, etc.). `graph_vcf.py` is optimized for use with structural variant VCFs, and has special handling for different SVTypes. BND events are plotted with both breakpoints; TRA events are skipped; etc. Despite being optimized for use with pbsv structural variant VCFs, most generic VCFs ought to work as well. **hg38 is used by default** but users may specify the path to another IGV genome.

For `graph_bed.py` and `graph_vcf.py`, users may add the `--bsub` flag to submit commands via LSF in parallel. The `--print` flag may be added to print commands instead of running them.

Primary use in Greg Cooper Lab: graphing structural variants from pacbio sequencing.




## Usage
Note that the python files have #! instructions to use the virtual environment at `/cluster/home/jlawlor/envs/igvgraph/` so the script should not be called using the `python` command, and using a version of python such as `module load g/python/3.6.0` will likely cause conflicts. If this occurs, `module unload` any currently-loaded python installations.

```
$ /cluster/lab/gcooper/igv-grapher/graph_vcf.py -h
usage: graph_vcf.py [-h] -v VCF -b BAMS [BAMS ...] [-g GENOME] [-p PREFIX] [-s SLOP] [-k BREAKPOINT_SLOP] [-n INDEL_BP_THRESHOLD] [-w MAX_WIDTH] [--print] [--bsub]

Use IGV to graph BED regions

optional arguments:
  -h, --help            show this help message and exit
  -v VCF, --vcf VCF     VCF input filename
  -b BAMS [BAMS ...], --bams BAMS [BAMS ...]
                        BAMS
  -g GENOME, --genome GENOME
                        Genome (hg19 or hg38)
  -p PREFIX, --prefix PREFIX
                        File prefix.
  -s SLOP, --slop SLOP  Slop: Number of bases to add at beginning and end of full graph
  -k BREAKPOINT_SLOP, --breakpoint-slop BREAKPOINT_SLOP
                        Number of bases to add at beginning and end of breakpoint graph
  -n INDEL_BP_THRESHOLD, --indel-bp-threshold INDEL_BP_THRESHOLD
                        Hide indels below this length.
  -w MAX_WIDTH, --max-width MAX_WIDTH
                        Largest width event to graph at once. (MB). Above this size will only graph breakpoints
  --print               Print commands instead of executing them
  --bsub                Submit via LSF to default queue with recommended resources.
```

```
$ /cluster/lab/gcooper/igv-grapher/graph_bed.py -h
usage: graph_bed.py [-h] -r BED [-t TITLE] -b BAMS [BAMS ...] [-g GENOME] [-p PREFIX] [-s SLOP] [-n INDEL_BP_THRESHOLD] [--print] [--bsub]

Use IGV to graph BED regions. Location:/cluster/lab/gcooper/igv-grapher

optional arguments:
  -h, --help            show this help message and exit
  -r BED, --bed BED     BED input filename
  -t TITLE, --title TITLE
                        BED title column
  -b BAMS [BAMS ...], --bams BAMS [BAMS ...]
                        BAMS
  -g GENOME, --genome GENOME
                        Genome (hg19 or hg38)
  -p PREFIX, --prefix PREFIX
                        File prefix.
  -s SLOP, --slop SLOP  Slop: Number of bases to add at beginning and end of graph
  -n INDEL_BP_THRESHOLD, --indel-bp-threshold INDEL_BP_THRESHOLD
                        Hide indels below this length.
  --print               Print commands instead of executing them
  --bsub                use bsub.
```


```
$ /cluster/lab/gcooper/igv-grapher/graph_region.sh -h
/cluster/lab/gcooper/igv-grapher/graph_region.sh -b BAM_PATH [-b BAM_PATH] [-v expand|squish|collapse] -r REGION [-c CHROMOSOME] [-s START] [-e END] -o OUTPUT_FILENAME [-n MIN_INDEL_TO_SHOW] [-g GENOME]  ..
```

## Changelog
**09/03/2021**: Significant modification of `graph_vcf.py` to make multi-graph PDFs instead of a JPG. Update IGV version to 2.11.0.
