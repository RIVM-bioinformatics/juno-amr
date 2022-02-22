rule runVirulencefinder:
    """Run VirulenceFinder for each sample"""
    input:
        #Samples retrieved from config.yaml
        fasta_sample = lambda wildcards: SAMPLES[wildcards.sample]["assembly"]

    output:
        output_dir = directory(OUT + "/results/virulencefinder/{sample}/")
    
    conda:
        "../../envs/virulencefinder.yaml"
    
    message:
        "Processing received fasta sample in virulencefinder"
        
    resources: 
        mem_gb=config["mem_gb"]["virulencefinder"]

    threads: config["threads"]["virulencefinder"]

    shell:
    #the sample name directory is not being made by virulence finder
        """
        mkdir -p {output.output_dir} && python3 bin/virulencefinder/virulencefinder.py -i {input.fasta_sample} -o {output.output_dir} -p /mnt/db/juno-amr/virulencefinderdb/ -x
        """
