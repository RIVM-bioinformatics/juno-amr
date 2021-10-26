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
    include:  "bin/rules/runAmrfinderplus.smk"
    include: "bin/rules/runVirulencefinder.smk"
    SAMPLE_NAME = config["samples_fasta"]

include: "bin/rules/makeResfinderSummary.smk"
include: "bin/rules/makePointfinderSummary.smk"
include: "bin/rules/makeVirulencefinderSummary.smk"
include: "bin/rules/makeAmrfinderplusSummary.smk"

#################################################################################
#####   Specify final output                                                #####
#################################################################################

if config["Parameters"]["species"] == "other":
    rule all:
        """ Main rule that starts the complete workflow """
        resources: 
            mem_mb=config["mem_mb"]

        input: 
            expand(OUT + "/results/summary/summary_amr_genes.csv"),
            expand(OUT + "/results/summary/summary_amr_phenotype.csv"),
            expand(OUT + "/results/summary/summary_virulencefinder.csv"),
            expand(OUT + "/results/summary/summary_amrfinderplus.csv"),
            expand(OUT + "/results/resfinder/{sample}", sample=SAMPLE_NAME),
            expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLE_NAME),
            expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLE_NAME)
else:
    rule all:
        """ Main rule that starts the complete workflow """
        resources: 
            mem_mb=config["mem_mb"]

        input:
            expand(OUT + "/results/summary/summary_amr_genes.csv"),
            expand(OUT + "/results/summary/summary_amr_phenotype.csv"),
            expand(OUT + "/results/summary/summary_virulencefinder.csv"),
            expand(OUT + "/results/summary/summary_amrfinderplus.csv"),
            expand(OUT + "/results/summary/summary_amr_pointfinder_results.csv"),
            expand(OUT + "/results/summary/summary_amr_pointfinder_prediction.csv"),
            expand(OUT + "/results/resfinder/{sample}", sample=SAMPLE_NAME),
            expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLE_NAME),
            expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLE_NAME)