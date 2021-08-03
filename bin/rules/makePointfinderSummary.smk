rule makePointfinderSummary:    
    input:
    #TODO make fasta or fastq
        resfinder_output_dir = expand(OUT + "/results_per_sample/{sample}", sample=SAMPLE_NAME)

    output:
        pointfinder_results = OUT + "/summary/summary_amr_pointfinder_results.csv",
        pointfinder_prediction = OUT + "/summary/summary_amr_pointfinder_prediction.csv"

    #conda: 
    #    "../../envs/resfinder.yaml"

    message:
        "Creating PointFinder summary file"
    
    resources:
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    params:
        species = config["Parameters"]["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sp {output.pointfinder_results} {output.pointfinder_prediction} -i {input.resfinder_output_dir} -st pointfinder"