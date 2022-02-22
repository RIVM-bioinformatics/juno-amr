rule makeAmrfinderplusSummary:    
    input:
        vir_output = expand(OUT + "/results/amrfinderplus/{sample}/", sample=SAMPLES)

    output:
        vir_summary = OUT + "/summary/summary_amrfinderplus.csv",

    message:
        "Creating Amrfinderplus summary file"
    
    resources:
        mem_gb=config["mem_gb"]["amrfinderplus"]

    threads: 
        config["threads"]["amrfinderplus"]

    params:
        species = config["species"]

    shell:
        "python3 bin/python_scripts/make_summary.py -sa {output.vir_summary} -i {input.vir_output} -st amrfinderplus"
