rule makePointfinderSummary:    
    input:
        resfinder_output_dir = expand(OUT + "/results_per_sample/{sample}", sample=SAMPLES)

    output:
        pointfinder_results = OUT + "/summary/summary_amr_pointfinder_results.csv",
        pointfinder_prediction = OUT + "/summary/summary_amr_pointfinder_prediction.csv"

    #conda: 
    #    "../../envs/resfinder.yaml"

    message:
        "Creating PointFinder summary file"
    
    resources:
        mem_mb=config["mem_mb"]["resfinder"]

    threads: 
        config["threads"]["resfinder"]

    params:
        species = config["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sp {output.pointfinder_results} {output.pointfinder_prediction} -i {input.resfinder_output_dir} -st pointfinder"