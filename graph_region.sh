#!/bin/bash
PATH=/cluster/software/utils/xvfb:$PATH
export IGV_MEM=16384m
GENOME="/cluster/lab/gcooper/igv-grapher/genomes/hg38/hg38.genome"
INDEL_BP_THRESHOLD=1
VIEW="expand"
prefix=`dirname $(readlink $0 || echo $0)`
#prefix=/cluster/lab/gcooper/software/IGV_Linux_2.11.0
usage(){
  echo "$0 -b BAM_PATH [-b BAM_PATH] [-v expand|squish|collapse] -r REGION [-c CHROMOSOME] [-s START] [-e END] -o OUTPUT_FILENAME [-n MIN_INDEL_TO_SHOW] [-g GENOME]  ..." >&2
  exit

}
while getopts b:g:o:n:hc:s:e:r:v: opt; do
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
		;;
		v ) VIEW=${OPTARG}
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
  if [[ ! (-f ${B}.bai || ${B}.tbi) ]]; then
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
"preference SAM.SMALL_INDEL_BP_THRESHOLD ${INDEL_BP_THRESHOLD}
new
genome ${GENOME}" >> ${COMMANDS_FILE}
for B in ${BAMPATHS[@]}; do
  echo "load ${B}" >> ${COMMANDS_FILE}
done
echo \
"goto ${CHROM}:${START}-${END}
${VIEW}
group tag HP
sort start
snapshot ${OUTPUT_FILENAME}
exit" \
>> ${COMMANDS_FILE}
#sed -i 's/-1=null/-1/' ~/igv/prefs.properties
xvfb-run-safe ${prefix}/igv.sh --batch ${COMMANDS_FILE}
