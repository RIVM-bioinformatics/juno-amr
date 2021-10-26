rule makeAmrfinderplusSummary:    
    input:
        vir_output = expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLE_NAME)

    output:
        vir_summary = OUT + "/results/summary/summary_amrfinderplus.csv",

    message:
        "Creating Amrfinderplus summary file"
    
    resources:
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    params:
        species = config["Parameters"]["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sa {output.vir_summary} -i {input.vir_output} -st amrfinderplus"