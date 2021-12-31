rule makeResfinderSummary:    
    input:
        resfinder_output_dir = expand(OUT + "/results_per_sample/{sample}", sample=SAMPLES)

    output:
        genes_summary = OUT + "/summary/summary_amr_genes.csv",
        pheno_summary = OUT + "/summary/summary_amr_phenotype.csv"

    #conda: 
    #    "../../envs/resfinder.yaml"

    message:
        "Creating ResFinder summary file"
    
    resources:
        mem_mb=config["mem_mb"]["resfinder"]

    threads: 
        config["threads"]["resfinder"]

    params:
        species = config["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sr {output.genes_summary} {output.pheno_summary} -i {input.resfinder_output_dir} -st resfinder"