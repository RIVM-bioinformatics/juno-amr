rule makeResfinderSummary:    
    input:
        resfinder_gene_output = expand(OUT + "/results_per_sample/{sample}/ResFinder_results_tab.txt", sample=config["samples_fastq_r1"]),
        resfinder_pheno_output = expand(OUT + "/results_per_sample/{sample}/pheno_table.txt", sample=config["samples_fastq_r1"])
    output:
        genes_summary = OUT + "/summary/summary_amr_genes.csv",
        pheno_summary = OUT + "/summary/summary_amr_phenotype.csv",

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