rule makeVirulencefinderSummary:
    input:
        vir_output=expand(OUT + "/results/virulencefinder/{sample}/", sample=SAMPLES),
    output:
        vir_summary=OUT + "/summary/summary_virulencefinder.csv",
    message:
        "Creating Virulencefinder summary file"
    resources:
        #TODO check if this needs other mem, same for other rules and threads as well
        mem_gb=int(config["mem_gb"]["virulencefinder"]),
    threads: int(config["threads"]["virulencefinder"])
    params:
        species=config["species"],
    shell:
        "python3 bin/make_summary.py -sv {output.vir_summary} -i {input.vir_output} -st virulencefinder"
