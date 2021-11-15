rule runVirulencefinder:
    """Run VirulenceFinder for each sample"""
    input:
        #Samples retrieved from config.yaml
        lambda wildcards: SAMPLE_NAME[wildcards.sample]

    output:
        output_dir = directory(OUT + "/results/virulencefinder/{sample}/")
    
    conda:
        "../../envs/virulencefinder.yaml"
    
    message:
        "Processing received fasta sample in virulencefinder"
        
    resources: 
        mem_mb=config["mem_mb"]

    threads: config["threads"]

    shell:
    #the sample name directory is not being made by virulence finder
        """
        mkdir -p {output.output_dir} && python3 bin/virulencefinder/virulencefinder.py -i {input} -o {output.output_dir} -p /mnt/db/juno-amr/virulencefinderdb/ -x
        """
