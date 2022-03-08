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
OUT = config["output_dir"]

include: "bin/rules/runResfinderFastq.smk"
include: "bin/rules/makeResfinderSummary.smk"
include: "bin/rules/makePointfinderSummary.smk"
include: "bin/rules/makeIlesSummary.smk"
#################################################################################
#####   Specify final output                                                #####
#################################################################################

localrules:
    all
#If the species is other, pointfinder cannot be run, so there will be no output expected of this part
# iles summary can only be created for ecoli, shigella, campylobacter and salmonella species
if config["species"] == "other":
    rule all:
        """ Main rule that starts the complete workflow """
        input: 
            expand(OUT + "/results_per_sample/{sample}", sample=SAMPLES),
            expand(OUT + "/summary/summary_amr_genes.csv"),
            expand(OUT + "/summary/summary_amr_phenotype.csv"),
 
else:
    species = config["species"]
    if species == "escherichia coli" or species == "shigella" or species == "campylobacter" or species == "salmonella":
        rule all:
            """ Main rule that starts the complete workflow """
            input:
                expand(OUT + "/results_per_sample/{sample}", sample=SAMPLES),
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv"),
                expand(OUT + "/summary/summary_iles.csv")
    else:
        rule all:
            """ Main rule that starts the complete workflow """
            input:
                expand(OUT + "/results_per_sample/{sample}", sample=SAMPLES),
                expand(OUT + "/summary/summary_amr_genes.csv"),
                expand(OUT + "/summary/summary_amr_phenotype.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
                expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv"),
