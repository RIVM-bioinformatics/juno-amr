rule runResfinderFasta:
    """Trying to run resfinder with hardcoded paths and all packages installed in a environment generated by conda/snakemake"""
    input:
        #Samples retrieved from config.yaml
        lambda wildcards: SAMPLE_NAME[wildcards.sample]

    output:
        #Make an output directory per sample
        output_dir = directory(OUT + "/results_per_sample/{sample}")
    
    #conda:
    #    "../../envs/resfinder.yaml"
    
    message:
        "Processing received fasta sample in ResFinder and PointFinder"

    params:
    #get parameters from configfile
        l = config["Parameters"]["coverage"],
        t = config["Parameters"]["threshold"],
        species = config["Parameters"]["species"],
        resfinder_db = config["Parameters"]["resfinder_db"],
        pointfinder_db = config["Parameters"]["pointfinder_db"],
        run_pointfinder = config["Parameters"]["run_pointfinder"]
        
    resources: 
        mem_mb=config["mem_mb"]

    threads: config["threads"]


    shell:
        # Command to call resfinder
        """
if [ {params.run_pointfinder} == "1" ]; then
    python3 bin/resfinder/run_resfinder.py -o {output.output_dir} -s \"{params.species}\" -l {params.l} -t {params.t} --acquired --point -ifa {input} -db_res {params.resfinder_db} -db_point {params.pointfinder_db}
else
    python3 bin/resfinder/run_resfinder.py -o {output.output_dir} -s \"{params.species}\" -l {params.l} -t {params.t} --acquired -ifa {input} -db_res {params.resfinder_db} -db_point {params.pointfinder_db}
fi
        """
