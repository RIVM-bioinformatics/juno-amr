rule runResfinderFastq:
    """Trying to run resfinder with hardcoded paths and all packages installed in a environment generated by conda/snakemake"""
    input:
        #Samples retrieved from config.yml
        lambda wildcards: config["samples_fastq_r1"][wildcards.sample],
        lambda wildcards: config["samples_fastq_r2"][wildcards.sample]

    output:
        #Output file requested by rule all
        output_file = OUT + "/results_per_sample/{sample}/ResFinder_results.txt",
        output_file_2 = OUT + "/results_per_sample/{sample}/pheno_table.txt",
        #Directory per sample
        output_dir = directory(OUT + "/results_per_sample/{sample}")
    
    conda:
    #TODO put this command in a config for easy access
        "../../envs/resfinder.yml"
    
    message:
        "Processing received samples in resfinder"

    params:
    #get parameters from configfile
        l = config["Parameters"]["coverage"],
        t = config["Parameters"]["threshold"],
        species = config["Parameters"]["species"],
        resfinder_db = config["Parameters"]["resfinder_db"],
        pointfinder_db = config["Parameters"]["pointfinder_db"],
        run_pointfinder = config["Parameters"]["run_pointfinder"]

    resources: 
    #TODO add to fasta
        mem_mb=config["mem_mb"]

#TODO add to fasta
    threads: config["threads"]

    shell:
    #TODO put this in a python script and run the script, this is ugly
    #TODO change this also for fasta if needed
    #TODO add KMA path/db
        # "python3 resfinder/run_resfinder.py -o {output.output_dir} -s \"{params.species}\" -l {params.l} -t {params.t} --acquired --point -ifq {input} -db_res {params.resfinder_db} -db_point {params.pointfinder_db}"
        """
if [ {params.run_pointfinder} == "1" ]; then
    python3 resfinder/run_resfinder.py -o {output.output_dir} -s \"{params.species}\" -l {params.l} -t {params.t} --acquired --point -ifq {input} -db_res {params.resfinder_db} -db_point {params.pointfinder_db}
else
    python3 resfinder/run_resfinder.py -o {output.output_dir} -s \"{params.species}\" -l {params.l} -t {params.t} --acquired -ifq {input} -db_res {params.resfinder_db} -db_point {params.pointfinder_db}
fi
        """
