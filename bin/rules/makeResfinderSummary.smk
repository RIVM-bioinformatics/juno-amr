rule makeResfinderSummary:
    """Make a summary of the output of resfinder"""
    input:
        resfinder_gene_output = OUT + "/results_per_sample/{sample}/ResFinder_results.txt", sample=config["samples_fastq_r1"]),
        #resfinder_pheno_output = OUT + "/results_per_sample/{sample}/pheno_table.txt", sample=config["samples_fastq_r1"])
    output:
        #pheno_summary = OUT + "summary/summary_amr_phenotype.csv",
        genes_summary = OUT + "summary/summary_amr_genes.csv"

    conda: 
        "../../envs/resfinder.yml"

    message:
        "Creating a summary file"
    
    resources:
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    script:
        "../python_scripts/make_summary.py"