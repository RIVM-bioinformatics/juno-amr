"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
"""

#################################################################################
#####   Import config file                                                  #####
#################################################################################
configfile: "config/user_parameters.yaml"
configfile: "config/database_config.yaml"

#output dir
OUT = config["Parameters"]["output_dir"]

#check if input is fastq or fasta
if config["Parameters"]["input_isfastq_boolean"]is True:
    include: "bin/rules/runResfinderFastq.smk"
    SAMPLE_NAME = config["samples_fastq_r1"]
else:
    include: "bin/rules/runResfinderFasta.smk"
    SAMPLE_NAME = config["samples_fasta"]

include: "bin/rules/makeResfinderSummary.smk"
include: "bin/rules/makePointfinderSummary.smk"
#################################################################################
#####   Specify final output                                                #####
#################################################################################

#If the species is other, pointfinder cannot be run, so there will be no output expected of this part
if config["Parameters"]["species"] == "other":
    rule all:
        """ Main rule that starts the complete workflow """
        resources: 
            mem_mb=config["mem_mb"]

        input: 
            expand(OUT + "/results_per_sample/{sample}", sample=SAMPLE_NAME),
            expand(OUT + "/summary/summary_amr_genes.csv"),
            expand(OUT + "/summary/summary_amr_phenotype.csv")
else:
    rule all:
        """ Main rule that starts the complete workflow """
        resources: 
            mem_mb=config["mem_mb"]

        input:
            expand(OUT + "/results_per_sample/{sample}", sample=SAMPLE_NAME),
            expand(OUT + "/summary/summary_amr_genes.csv"),
            expand(OUT + "/summary/summary_amr_phenotype.csv"),
            expand(OUT + "/summary/summary_amr_pointfinder_results.csv"),
            expand(OUT + "/summary/summary_amr_pointfinder_prediction.csv")
        
