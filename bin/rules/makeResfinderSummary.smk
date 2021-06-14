rule makeResfinderSummary:    
    input:
    #TODO make fasta or fastq
        resfinder_output_dir = expand(OUT + "/results_per_sample/{sample}", sample=SAMPLE_NAME)

    output:
        genes_summary = OUT + "/summary/summary_amr_genes.csv",
        pheno_summary = OUT + "/summary/summary_amr_phenotype.csv",
        pointfinder_results = OUT + "/summary/summary_amr_pointfinder_results.csv",
        pointfinder_prediction = OUT + "/summary/summary_amr_pointfinder_prediction.csv"

    conda: 
        "../../envs/resfinder.yaml"

    message:
        "Creating a summary file"
    
    resources:
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    shell:
        "python3 bin/python_scripts/make_summary.py -s {output.genes_summary} {output.pheno_summary} {output.pointfinder_results} {output.pointfinder_prediction} -i {input.resfinder_output_dir}"