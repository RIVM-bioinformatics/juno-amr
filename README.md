<div align="center">
    <h1> Juno-amr</h1>
    <br />
    <h2> Pipeline for antimicrobial restistance</h2>
    <br />
    <img src="https://via.placeholder.com/150" alt="pipeline logo">
</div>

## Pipeline information
* **Author(s):**             Roxanne Wolthuis
* **Organization:**         Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
* **Department:**           Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
* **Start date:**           30 - 03 - 2021
* **Commissioned by:**      -

## About this project
This pipeline automates the tools Resfinder and Pointfinder.

## Prerequisities
* **Python3.5** or newer. Python is the scripting language used to create the program.
https://www.python.org/downloads/

## Installation
1. Clone the repository.
```
git clone https://github.com/RIVM-bioinformatics/Juno-amr.git
```

2. Go to Juno directory.
```
cd Juno-amr
```

3. Activate mamba.
```
conda activate mamba
```

4. Create mamba environment.
```
mamba env create -f envs/juno_amr_master.yml
```

5. Activate the environment,
```
conda activate juno-amr_master
```

6. [need to test again if these steps are still correct]
```
test
```

## Usage
The base command to run this program. Its important that there is no slash after the input folder
```
python3 juno-amr.py -s [species] -i [dir/to/fasta_or_fastq_files
```

An example on how to run the pipeline.
```
python3 juno-amr.py -s salmonella -i dir/to/fastq_files -o output -l 0.8 -t 0.6
```

For detailed information please visit the [documentation](https://www.google.com "Pipeline documentation").

## Parameters
### Command for help
* ```-h, --help``` Shows the help of the pipeline

#### Required parameters
* ```-i, --input``` Path to the directory of your input. Can be fasta files or paired fastq files. It is important to link to the directory and not the files. Don't put a slash behind the last directory.
* ```-s --species**``` Full scientific name of the species sample. Use underscores between the parts of a name and not spaces. A list of available species can be shown if you type ```python3 juno-amr.py -s -h```. It is possible to select 'other' as a species, if 'other' is selected the pipeline will only run resfinder

### Optional parameters
* ```-l --min_cov```    Minimum coverage of resfinder
* ```-t --threshold```  Threshold for identity of resfinder
* ```-o, --output```    Path to the directory that is used for the output. If none is given the default will be an output directory in the Juno-amr folder.
* ```-n --dryrun```     If you want to run a dry run use one of these parameters
* ```-db_point```       Path for alternative database for pointfinder
* ```-db_res```         Path for alternative database for resfinder
* ```--point```         Type one to run pointfinder, type 0 to not run pointfinder. By default pointfinder will always run if there is a species selected.

## Content of this repository
* **bin:**
    This folder contains all the scripts separated in Python scripts and rules for snakemake.
    * **python_scripts:**
        * **make_summary.py:** Creates the four produced summary files
    * **rules:**
        * **makeResfinderSummary.smk:** Calls on snakemake to produce summary files by running make_summary.py
        * **runResfinderFasta.smk:** Calls on snakemake to produce resfinder and pointfinder output with juno-amr.py based on fasta input
        * **runResfinderFastq.smk:** Calls on snakemake to produce resfinder and pointfinder output with juno-amr.py based on fastq input
* **config:**
    * **database_config.yml:** Consists of all settings for to run on the cluster?
    * **setup_config_fa.yml:** Template that is used to generate a config with parameters from the argumentparse for fasta input
    * **setup_config.fq.yml:** Template that is used to generate a config with parameters from the argumentparse for fastq input
* **envs:**
    * **juno_amr_master.yml:** To setup the juno environment
    * **resfinder.yml:** To setup resfinder and pointfinder
* **.gitignore:** File with files and directories to be ignored by git
* **License:** AGPL3/Free software license
* **README.md:** To create the readme
* **Snakefile:** The main snakefile with a rule all that calls the other rules based on the input type
* **juno-amr.py:** The wrapper for this pipeline

## Explanation of the output
* **log:** Log with output and error file from the cluster for each snakemake rule/step that is performed
* **results_per_sample:** Output produced by resfinder and pointfinder for each sample
* **summary:** Directory with 4 summary files created from each sample within the results_per_sample folder

## Issues
* For now this only works on the cluster.
* Parameters need to be filled in as asked, error handling is not optimalized yet.

## Future ideas for this pipeline
* Make this pipeline available and user friendly for users outside RIVM.

## License

## Contact

## Achknowledgements