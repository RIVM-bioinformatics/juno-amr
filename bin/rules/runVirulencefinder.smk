rule runVirulencefinder:
    """Run VirulenceFinder for each sample"""
    input:
        fasta_sample=lambda wildcards: SAMPLES[wildcards.sample]["assembly"],
    output:
        output_dir=directory(OUT + "/results/virulencefinder/{sample}/"),
    conda:
        "../../envs/virulencefinder.yaml"
    message:
        "Processing received fasta sample in virulencefinder"
    resources:
        mem_gb=int(config["mem_gb"]["virulencefinder"]),
    threads: int(config["threads"]["virulencefinder"])
    shell:
        #the sample name directory is not being made by virulence finder
        # t =
        # l = 
        """
        mkdir -p {output.output_dir} && python3 bin/virulencefinder/virulencefinder.py -i {input.fasta_sample} -o {output.output_dir} -p /mnt/db/juno-amr/virulencefinderdb/ -x 
        """
