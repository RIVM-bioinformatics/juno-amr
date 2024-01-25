rule runamrfinderplus:
    """Run amrfinderplus"""
    input:
       fasta_sample = lambda wildcards: SAMPLES[wildcards.sample]["assembly"]

    output:
        output_dir = directory(OUT + "/results/amrfinderplus/{sample}/")        
    
    conda:
        "../../envs/amrfinderplus.yaml"

    message:
        "Processing received fasta sample(s) in amrfinderplus"

    resources: 
        mem_gb=int(config["mem_gb"]["amrfinderplus"])

    threads: int(config["threads"]["amrfinderplus"])
    
    shell:
    #TODO amrfinder needs to be run with -u in order to update
    #This needs to be done the first time an environment is created or anytime you want to update
    #Do this with a boolean or?
    #amrfinder -u
    #mkdir -p {output.output_dir} && amrfinder -n {input.fasta_sample} --plus -o {output.output_dir}/amrfinder_result.txt
    #amrfinder cannot be run with -p or -n, just run it as a separate command
        """
        mkdir -p {output.output_dir} && amrfinder -n {input.fasta_sample} --plus -o {output.output_dir}/amrfinder_result.txt -d /mnt/db/juno-amr/amrfinderplusdb/2022-12-19.1
        """
