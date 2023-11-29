rule makeIlesSummary:    
    input:
        resfinder_output_dir = expand(OUT + "/results/resfinder/{sample}", sample=SAMPLES)

    output:
        iles_summary = OUT + "/summary/summary_iles.csv",

    message:
        "Creating iles summary file"
    
    resources:
        mem_gb=config["mem_gb"]["resfinder"]

    threads: 
        config["threads"]["resfinder"]

    params:
        species = config["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -si {output.iles_summary} -i {input.resfinder_output_dir} -st iles"