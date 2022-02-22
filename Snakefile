"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
"""

#################################################################################
#####   Imports and configuration                                           #####
#################################################################################
import os
import yaml

#collect samples
sample_sheet = config["sample_sheet"]
SAMPLES = {}
with open(sample_sheet) as sample_sheet_file:
    SAMPLES = yaml.safe_load(sample_sheet_file) 

#output dir
#TODO check which one of these to keep
OUT = config["output_dir"]
#OUT = config["Parameters"]["output_dir"]

#check if input is fastq or fasta
#TODO check if this is necessary
# if config["input_isfastq_boolean"]is True:
#     include: "bin/rules/runResfinderFastq.smk"
#     #SAMPLE_NAME = config["samples_fastq_r1"]
# else:
#     include: "bin/rules/runResfinderFasta.smk"
#     include: "bin/rules/runAmrfinderplus.smk"
#     include: "bin/rules/runVirulencefinder.smk"
    #SAMPLE_NAME = config["samples_fasta"]

include: "bin/rules/runResfinderFastq.smk"
include: "bin/rules/makeResfinderSummary.smk"
include: "bin/rules/makePointfinderSummary.smk"
include: "bin/rules/makeVirulencefinderSummary.smk"
include: "bin/rules/makeAmrfinderplusSummary.smk"
include: "bin/rules/runResfinderFasta.smk"
include: "bin/rules/runAmrfinderplus.smk"
include: "bin/rules/runVirulencefinder.smk"

#################################################################################
#####   Specify final output                                                #####
#################################################################################

#TODO check if main works
if ["species"] == "other":
    if config["input_isfastq_boolean"] is False:
        rule all:
            """ Main rule that starts the complete workflow """
            input: 
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES),
                expand(OUT + "/summary/summary_virulencefinder.csv"),
                expand(OUT + "/summary/summary_amrfinderplus.csv"),
                expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLES),
                expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLES)
    else:
        rule all:
            """ Main rule that starts the complete workflow """
            input: 
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES)
else:
    if config["input_isfastq_boolean"]is False:
        rule all:
            """ Main rule that starts the complete workflow """
            input:
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv"),
                expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES),
                expand(OUT + "/summary/summary_virulencefinder.csv"),
                expand(OUT + "/summary/summary_amrfinderplus.csv"),
                expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLES),
                expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLES)

    else:
        rule all:
            """ Main rule that starts the complete workflow """
            input:
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv"),
                expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES)
