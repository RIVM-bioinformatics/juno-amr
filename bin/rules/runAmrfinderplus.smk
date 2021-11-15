rule runamrfinderplus:
    """Run amrfinderplus"""
    input:
        lambda wildcards: SAMPLE_NAME[wildcards.sample]

    output:
        output_dir = directory(OUT + "/results/amrfinderplus/{sample}/")        
    
    conda:
        "../../envs/amrfinderplus.yaml"

    message:
        "Processing received fasta sample(s) in amrfinderplus"

    resources: 
        mem_mb=config["mem_mb"]

    threads: config["threads"]
    
    shell:
    #TODO amrfinder needs to be run with -u in order to update
    #This needs to be done the first time an environment is created or anytime you want to update
    #Do this with a boolean or?
    #amrfinder -u
        """
        mkdir -p {output.output_dir} && amrfinder -n {input} --plus -o {output.output_dir}/amrfinder_result.txt
        """
