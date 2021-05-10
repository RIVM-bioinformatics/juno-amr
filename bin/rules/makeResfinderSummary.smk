rule makeResfinderSummary:
    """Make a summary of the output of resfinder"""
    input:
        # alle samples die uit resfinder komen
    output:
        # de summary file(s)
        # Dit is de input voor de rule all

    conda: 
        #Enter the environment
        # is this neccessary?
        #TODO make a easy access command for this path
        "../../envs/resfinder.yml"

    message:
        "Creating a summary file"
    
    resources:
        #Check if this is neccessary
        mem_mb=config["mem_mb"]

    threads: 
        config["threads"]

    script:
        #call here the python script with the summary function