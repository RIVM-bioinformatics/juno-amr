<div align="center">
    <h1> Juno-AMR</h1>
    <br />
    <h2> Pipeline for antimicrobial resistance</h2>
    <br />
    <img src="files/juno_antimicrobial_lightbg.png" alt="pipeline logo">
</div>

## Pipeline information
* **Author(s):**            Roxanne Wolthuis, Alejandra Hernandez Segura, Maaike van den Beld
* **Organization:**         Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
* **Department:**           Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
* **Start date:**           30 - 03 - 2021
* **Commissioned by:**      Maaike van den Beld

## About this project
The Juno Antimicrobial Resistance(Juno AMR) pipeline is a pipeline that is used to automate multiple antimicrobial resistance related tools. 

The tools used in this pipeline:

[ResFinder](https://bitbucket.org/genomicepidemiology/resfinder/src/master/) - created by [The Center For Genomic Epidemiology](https://www.genomicepidemiology.org/)

[PointFinder](https://bitbucket.org/genomicepidemiology/pointfinder/src/master/) - created by [The Center For Genomic Epidemiology](https://www.genomicepidemiology.org/)

[VirulenceFinder](https://bitbucket.org/genomicepidemiology/virulencefinder/src/master/) - created by [The Center For Genomic Epidemiology](https://www.genomicepidemiology.org/)

[AMRFinderPlus](https://github.com/ncbi/amr) - created by [The National Center for Biotechnology Information](https://www.ncbi.nlm.nih.gov/)

These tools help identify: acquired antimicrobial resistance genes, chromosomal mutations mediating antimicrobial resistance, virulence factors, biocide, heat, acid, and metal resistance genes. The input can be partial or total DNA sequences of bacteria. The output of the tools can be used for analysis and is also combined in multiple summary files for a quick overview of the most important results.

## Prerequisities
* **Linux environment**
* **(mini)conda**
* **Python3.7.6** Python is the scripting language used to create the program.


## Installation
1. Clone the repository.
```
git clone https://github.com/RIVM-bioinformatics/juno-amr.git
```

2. Go to Juno directory.
```
cd juno-amr
```

3. Create & activate mamba environment.
```
conda env update -f envs/mamba.yaml
```
```
conda activate mamba
```

4. Create & activate juno environment.
```
mamba env update -f envs/juno_amr.yaml
```
```
conda activate juno-amr_master
```

7. Example of run:
```
python3 juno-amr.py -i [input] -o [output] -s [species]
```

**Note:** To get an overview of the available species for chromosomal point mutations use the command:
```
python3 juno-amr.py --help-species
```

## Parameters & Usage
### Command for help
* ```-h, --help``` Shows the help of the pipeline

### Required parameters
* ```-i, --input``` Path to the directory of your input. Can be fasta files and paired fastq files combined in one directory or the output directory of the Juno-assembly pipeline. It is important to link to the directory and not the files.
* ```-s --species**``` Full scientific name of the species sample. Use underscores between the parts of a name and not spaces. A list of available species can be shown if you type ```python3 juno-amr.py --species-help```. It is possible to select 'other' as a species, if 'other' is selected the pipeline will only run ResFinder

### Optional parameters
* ```-l --min_cov```    Minimum coverage of ResFinder
* ```-t --threshold```  Threshold for identity of ResFinder
* ```-o, --output```    Path to the directory that is used for the output. If none is given the default will be an output directory in the juno-amr folder.
* ```-n --dryrun```     If you want to run a dry run use one of these parameters
* ```-db_point```       Path for alternative database for PointFinder
* ```-db_res```         Path for alternative database for ResFinder
* ```--point```         Type one to run PointFinder, type 0 to not run PointFinder. By default PointFinder will always run if there is a species selected.


### The base command to run this program. 
```
python3 juno-amr.py -s [species] -i [dir/to/fasta_and_fastq_files]
```
```
python3 juno-amr.py -s [species] -i [dir/to/juno_assembly_output]
```

### An example on how to run the pipeline.
```
python3 juno-amr.py -s salmonella -i dir/to/fastq_and_fasta_files -o output -l 0.8 -t 0.6
```

Detailed information about the pipeline can be found in the [documentation](https://www.google.com "Pipeline documentation"). This documentation is only accessible for users that have access to the RIVM Linux environment.

## Explanation of the output
* **log:** Log with output and error file from the cluster for each Snakemake rule/step that is performed
* **results_per_sample:** Output produced by ResFinder and PointFinder for each sample
* **summary:** Directory with 4 summary files created from each sample within the results_per_sample folder

## Issues
* For now this only works on the RIVM cluster.
* Parameters need to be filled in as asked, error handling is not optimized yet.

## Future ideas for this pipeline
* Make this pipeline available and user friendly for users outside RIVM.
* Make documentation available outside RIVM.

## License
This pipeline is licensed with a AGPL3 license. Detailed information can be found inside the 'LICENSE' file in this repository.

## Contact
* **Contact person:**       Roxanne Wolthuis
* **Email**                 roxanne.wolthuis@rivm.nl  

## Acknowledgements
