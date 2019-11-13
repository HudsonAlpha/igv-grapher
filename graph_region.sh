#!/bin/bash
PATH=/gpfs/gpfs2/software/utils/xvfb/:/gpfs/gpfs2/software/igv-2.4.13/$PATH
IGV_MEM=16384m
GENOME="hg38"
INDEL_BP_THRESHOLD=1
usage(){
  echo "$0 -b BAM_PATH [-b BAM_PATH] -r REGION [-c CHROMOSOME] [-s START] [-e END] -o OUTPUT_FILENAME [-n MIN_INDEL_TO_SHOW] [-g GENOME]  ..." >&2
  exit

}
while getopts b:g:o:n:hc:s:e:r: opt; do
        case ${opt} in
                b ) BAMPATHS+=("${OPTARG}")
                ;;
                c ) CHROM=${OPTARG}
                ;;
                s ) START=${OPTARG}
                ;;
                e ) END=${OPTARG}
                ;;
                g ) GENOME=${OPTARG}
                ;;
                o ) OUTPUT_FILENAME=${OPTARG}
                ;;
                n ) INDEL_BP_THRESHOLD=${OPTARG}
                ;;
                h ) usage
                ;;
                r ) REGION=${OPTARG}
        esac
done

if [[ -z ${BAMPATHS[@]} ]]; then
  echo "No bam path supplied."
fi
for B in ${BAMPATHS[@]}; do
  if [[ ! -f $B ]]; then
    echo "Supplied bam ${B} does not exist."
    exit 1
  fi
  if [[ ! -f ${B}.bai ]]; then
    echo "Supplied bam ${B} is not indexed."
    exit 1
  fi
done
if [[ -z $OUTPUT_FILENAME ]]; then
  echo "No output file"
  exit 1
fi
COMMANDS_FILE=$(mktemp)

if [[ -n "$REGION" ]]; then
  CHROM=$(echo $REGION | awk -F ":" '{print $1}')
  START=$(echo $REGION | awk -F ":" '{print $2}' | awk -F "-" '{print $1}')
  END=$(echo $REGION | awk -F ":" '{print $2}' | awk -F "-" '{print $2}')
fi

echo \
"preference SAM.MAX_VISIBLE_RANGE 1000000
preference SAM.SHOW_CENTER_LINE true
preference SAM.SMALL_INDEL_BP_THRESHOLD ${INDEL_BP_THRESHOLD}
new
genome ${GENOME}" >> ${COMMANDS_FILE}
for B in ${BAMPATHS[@]}; do
  echo "load ${B}" >> ${COMMANDS_FILE}
done
echo \
"goto ${CHROM}:${START}-${END}
expand
sort quality
snapshot ${OUTPUT_FILENAME}
exit" \
>> ${COMMANDS_FILE}
xvfb-run-safe /gpfs/gpfs2/software/igv-2.4.13/igv.sh --batch ${COMMANDS_FILE}
