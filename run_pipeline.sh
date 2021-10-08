#!/bin/bash

# Wrapper for juno typing pipeline

set -euo pipefail

#----------------------------------------------#
# User parameters
#input_dir="${1%/}"
#output_dir="${2%/}"
#PROJECT_NAME="${irods_input_projectID}"

if [ ! -z "${1}" ] || [ ! -z "${2}" ] || [ ! -z "${irods_input_projectID}" ]
then
   INPUTDIR="${1}"
   output_dir="${2}"
   PROJECT_NAME="${irods_input_projectID}"
else
    echo "One of the parameters is missing, make sure there is an input directory, output directory and project name(param 1, 2 or irods_input_projectID)."
    exit 1
fi

if [ ! -d "${input_dir}" ] || [ ! -d "${output_dir}" ]
then
    echo "The input directory $input_dir or output directory $output_dir does not exist"
    exit 1
fi

case $PROJECT_NAME in

  adhoc|gasadhoc|bacid|rogas|svgasuit|bsr_rvp)
    GENUS_ALL="other"
    ;;
  dsshig|svshig)
    GENUS_ALL="Shigella"
    ;;
  salm|svsalent|svsaltyp)
    GENUS_ALL="Salmonella"
    ;;
  svlismon)
    GENUS_ALL="Listeria"
    ;;
  svstec)
    GENUS_ALL="Escherichia"
    ;;
  campy)
    GENUS_ALL="Campylobacter"
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

python juno-amr.py --queue "${QUEUE}" -i "${input_dir}" -o "${output_dir}" -s "${GENUS_ALL}"

result=$?

exit ${result}
# Produce svg with rules
# snakemake --config sample_sheet=config/sample_sheet.yaml \
#             --configfiles config/pipeline_parameters.yaml config/user_parameters.yaml \
#             -j 1 --use-conda \
#             --rulegraph | dot -Tsvg > files/DAG.svg