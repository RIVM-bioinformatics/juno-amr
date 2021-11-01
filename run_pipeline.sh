#!/bin/bash

# Wrapper for juno AMR pipeline

set -euo pipefail

#----------------------------------------------#
# User parameters
if [ ! -z "${1}" ] || [ ! -z "${2}" ] || [ ! -z "${irods_input_projectID}" ]
then
   input_dir="${1}"
   output_dir="${2}"
   PROJECT_NAME="${irods_input_projectID}"
else
    echo "One of the parameters is missing, make sure there is an input directory, output directory and project name(param 1, 2 or irods_input_projectID)."
    exit 1
fi

if [ ! -d "${input_dir}" ] || [ ! -d "${output_dir}" ] || [ ! -d "${input_dir}/clean_fastq" ]
then
  echo "The input directory $input_dir, output directory $output_dir or fastq dir ${input_dir}/clean_fastq does not exist"
  exit 1
else
  input_fastq="${input_dir}/clean_fastq"
fi

case $PROJECT_NAME in

  adhoc|gasadhoc|bacid|rogas|svgasuit)
    GENUS_ALL="other"
    ;;
  dsshig|svshig)
    GENUS_ALL="escherichia_coli"
    ;;
  salm|svsalent|svsaltyp|vdl_salm)
    GENUS_ALL="salmonella"
    ;;
  svlismon|vdl_list)
    GENUS_ALL="other"
    ;;
  svstec|vdl_ecoli|vdl_stec)
    GENUS_ALL="escherichia_coli"
    ;;
  campy|vdl_campy)
    GENUS_ALL="campylobacter"
    ;;
  *)
    GENUS_ALL="other"
    ;;
    
esac


#----------------------------------------------#
# Create/update necessary environments
PATH_MAMBA_YAML="envs/mamba.yaml"
PATH_MASTER_YAML="envs/juno_amr_master.yaml"
MAMBA_NAME=$(head -n 1 ${PATH_MAMBA_YAML} | cut -f2 -d ' ')
MASTER_NAME=$(head -n 1 ${PATH_MASTER_YAML} | cut -f2 -d ' ')

echo -e "\nUpdating necessary environments to run the pipeline..."

# Removing strict mode because it sometimes breaks the code for 
# activating an environment and for testing whether some variables
# are set or not
set +euo pipefail 

conda env update -f "${PATH_MAMBA_YAML}"
source activate "${MAMBA_NAME}"

mamba env update -f "${PATH_MASTER_YAML}"

source activate "${MASTER_NAME}"

#----------------------------------------------#
# Run the pipeline

echo -e "\nRun pipeline..."

if [ ! -z ${irods_runsheet_sys__runsheet__lsf_queue} ]; then
    QUEUE="${irods_runsheet_sys__runsheet__lsf_queue}"
else
    QUEUE="bio"
fi

set -euo pipefail

python juno-amr.py --queue "${QUEUE}" -i "${input_dir}/clean_fastq/" -o "${output_dir}" -s "${GENUS_ALL}"

result=$?

# Propagate metadata
# SEQ_KEYS=
# SEQ_ENV=`env | grep irods_input_sequencing`
# for SEQ_AVU in ${SEQ_ENV}
# do
#     SEQ_KEYS="${SEQ_KEYS} ${SEQ_AVU%%=*}"
# done

# for key in $SEQ_KEYS irods_input_illumina__Flowcell irods_input_illumina__Instrument \
#     irods_input_illumina__Date irods_input_illumina__Run_number irods_input_illumina__Run_Id
# do
#     if [ ! -z ${!key} ] ; then
#         attrname=${key:12}
#         attrname=${attrname/__/::}
#         echo "${attrname}: '${!key}'" >> ${OUTPUTDIR}/metadata.yml
#     fi
# done

exit ${result}
# Produce svg with rules
# snakemake --config sample_sheet=config/sample_sheet.yaml \
#             --configfiles config/pipeline_parameters.yaml config/user_parameters.yaml \
#             -j 1 --use-conda \
#             --rulegraph | dot -Tsvg > files/DAG.svg