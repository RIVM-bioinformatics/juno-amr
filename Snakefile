"""
Juno-amr
Authors: Roxanne Wolthuis, Alejandra Hernandez Segura, Maaike van den Beld
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

#includes
include: "bin/rules/runResfinderFastq.smk"
include: "bin/rules/runAmrfinderplus.smk"
include: "bin/rules/runVirulencefinder.smk"
include: "bin/rules/makeResfinderSummary.smk"
include: "bin/rules/makePointfinderSummary.smk"
include: "bin/rules/makeVirulencefinderSummary.smk"
include: "bin/rules/makeAmrfinderplusSummary.smk"
#TODO this rule is out of use because we only run resfinder on fastq files
#include: "bin/rules/runResfinderFasta.smk"

#################################################################################
#####   Specify final output                                                #####
#################################################################################

if config["species"] == "other":
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
            expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
            expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv"),
            expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES),
            expand(OUT + "/summary/summary_virulencefinder.csv"),
            expand(OUT + "/summary/summary_amrfinderplus.csv"),
            expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLES),
            expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLES)