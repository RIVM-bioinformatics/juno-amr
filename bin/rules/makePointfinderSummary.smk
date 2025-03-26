rule makePointfinderSummary:    
    input:
        resfinder_output_dir = expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES)

    output:
        pointfinder_results = OUT + "/summary/summary_amr_pointfinder_results.csv",
        # pointfinder_prediction = OUT + "/summary/summary_amr_pointfinder_prediction.csv"

    message:
        "Creating PointFinder summary file"
    
    resources:
        mem_gb=int(config["mem_gb"]["resfinder"])

    threads: 
        int(config["threads"]["resfinder"])

    params:
        species = config["species"]

    shell:
        "python3 bin/make_summary.py -sp {output.pointfinder_results} -i {input.resfinder_output_dir} -st pointfinder"