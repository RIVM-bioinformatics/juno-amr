rule makeResfinderSummary:    
    input:
    #TODO make fasta or fastq
        resfinder_output_dir = expand(OUT + "/results/resfinder/{sample}", sample=SAMPLE_NAME)

    output:
        #hier gaat het nog fout
        genes_summary = OUT + "/results/summary/summary_amr_genes.csv",
        pheno_summary = OUT + "/results/summary/summary_amr_phenotype.csv"

    #conda: 
    #    "../../envs/resfinder.yaml"

    message:
        "Creating ResFinder summary file"
    
    resources:
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    params:
        species = config["Parameters"]["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sr {output.genes_summary} {output.pheno_summary} -i {input.resfinder_output_dir} -st resfinder"