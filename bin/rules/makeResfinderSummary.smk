rule makeResfinderSummary:    
    input:
        resfinder_output_dir = expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES)

    output:
        genes_summary = OUT + "/summary/summary_amr_genes.csv",
        pheno_summary = OUT + "/summary/summary_amr_phenotype.csv"

    message:
        "Creating ResFinder summary file"
    
    resources:
        mem_gb=config["mem_gb"]["resfinder"]

    threads: 
        config["threads"]["resfinder"]

    params:
        species = config["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sr {output.genes_summary} {output.pheno_summary} -i {input.resfinder_output_dir} -st resfinder"