"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

import sys
import argparse
import os
import re
import snakemake
import yaml
import pathlib
from pathlib import Path
import shutil
from ruamel.yaml import YAML
import csv
import pandas as pd

sys.path.insert(0, 'bin/python_scripts/')
from start_pipeline import *
from download_dbs import * 

class JunoAmrWrapper:
    def __init__(self, input_dir):
        """constructor, containing all variables"""
        #arguments=None
        #self.path_to_pointfinder_db = "/mnt/db/juno-amr/pointfinderdb"
        #input_dir = dict_arguments["input_dir"]
        self.input_dir = pathlib.Path(input_dir)



    # Start juno pipeline ale function 
    def start_juno_pipeline(self):
        '''
        This function performs calls other functions in the class to complete 
        all the necessary steps needed for a robust and well documented Juno
        pipeline. For instance, validating directories, making sample_dict 
        (from which a sample_sheet can be made), etc. This is the main (and 
        often only) function that is usually needed to run a Juno pipeline
        '''
        print("start juno")
        #print(self.input_dir)
        self.supported_extensions = {'fastq': ('.fastq', '.fastq.gz', '.fq', '.fq.gz'),
                                    'fasta': ('.fasta')}
        self.__subdirs_ = self.__define_input_subdirs()
        self.__validate_input_dir()
        print("Making a list of samples to be processed in this pipeline run...")
        self.sample_dict = self.make_sample_dict()
        print("Validating that all expected input files per sample are present in the input directory...")
        self.validate_sample_dict()
    
    def __validate_input_dir(self):
        '''
        Function to check that input directory is indeed an existing directory 
        that contains files with the expected extension (fastq or fasta)
        '''
        if self.input_type == 'both':
            fastq_subdir_validated = self.__validate_input_subdir(self.__subdirs_['fastq'], 
                                                                self.supported_extensions['fastq'])
            fasta_subdir_validated = self.__validate_input_subdir(self.__subdirs_['fasta'], 
                                                                self.supported_extensions['fasta'])
            return (fastq_subdir_validated and fasta_subdir_validated)
        else:
            return self.__validate_input_subdir(self.__subdirs_[self.input_type], 
                                                self.supported_extensions[self.input_type])


    #check if input dir is juno assembly output
    def __input_dir_is_juno_assembly_output(self):
        '''
        Function to check whether the input directory is actually the output 
        of the Juno_assembly pipeline. The Juno_assembly pipeline is often the 
        first step for downstream analyses, so its output becomes the input 
        directory of other pipelines
        '''
        is_juno_assembly_output = (self.input_dir.joinpath('clean_fastq').exists() 
                                        and self.input_dir.joinpath('de_novo_assembly_filtered').exists())
        if is_juno_assembly_output:
            return True
        else:
            return False

    #function to check if the input from juno assembly or regular input
    def __define_input_subdirs(self):
        '''
        Function to check whether the input is from the Juno assembly 
        pipeline or just a simple input directory
        '''
        # Only when the input_dir comes from the Juno-assembly pipeline 
        # the fastq and fasta files do not need to be in the same 
        # folder (fastq are then expected in a subfolder called 
        # <input_dir>/clean_fastq and the fasta assembly files are
        # expected in a subfolder called <input_dir>/de_novo_assembly_filtered)
        if self.__input_dir_is_juno_assembly_output():
            return {'fastq': self.input_dir.joinpath('clean_fastq'),
                    'fasta': self.input_dir.joinpath('de_novo_assembly_filtered')}
        else:
            return {'fastq': self.input_dir,
                    'fasta': self.input_dir}

    # Function to make sample dict --> yses enlist_fastq and enlist_fasta function
    def make_sample_dict(self):
        '''
        Function to make a sample sheet from the input directory (expecting 
        either fastq or fasta files as input)
        '''
        print("start make dict")
        if self.input_type == 'fastq':
            samples = self.__enlist_fastq_samples()
        elif self.input_type == 'fasta':
            samples = self.__enlist_fasta_samples()
        else:
            samples = self.__enlist_fastq_samples()
            samples_fasta = self.__enlist_fasta_samples()
            for k in samples.keys():
                samples[k]['assembly'] = samples_fasta[k]['assembly']
        return samples

    #makes fastq/fasta/orboth sample dicts
    def __enlist_fastq_samples(self):
        '''
        Function to enlist the fastq files found in the input directory. 
        Returns a dictionary with the form:
        {sample: {R1: fastq_file1, R2: fastq_file2}}
        '''
        # Regex to detect different sample names in de fastq file names
        # It does NOT accept sample names that contain _1 or _2 in the name
        # because they get confused with the identifiers of forward and reverse
        # reads.
        print("enlist fastq")
        pattern = re.compile("(.*?)(?:_S\d+_|_S\d+.|_|\.)(?:_L555_)?(?:p)?R?(1|2)(?:_.*\.|\..*\.|\.)f(ast)?q(\.gz)?")
        samples = {}
        for file_ in self.__subdirs_['fastq'].iterdir():
            if self.validate_file_has_min_lines(file_, self.min_num_lines):
                match = pattern.fullmatch(file_.name)
                if match:
                    sample = samples.setdefault(match.group(1), {})
                    sample[f"R{match.group(2)}"] = str(file_)        
        return samples

    def __enlist_fasta_samples(self):
        '''
        Function to enlist the fasta files found in the input 
        directory. Returns a dictionary with the form 
        {sample: {assembly: fasta_file}}
        '''
        print("enlist fasta")
        pattern = re.compile("(.*?).fasta")
        samples = {}
        for file_ in self.__subdirs_['fasta'].iterdir():
            if self.validate_file_has_min_lines(file_, self.min_num_lines):
                match = pattern.fullmatch(file_.name)
                if match:
                    sample = samples.setdefault(match.group(1), {})
                    sample["assembly"] = str(file_)
        return samples  

    #function that is used in enlist functions above
    def validate_file_has_min_lines(self, file_path, min_num_lines=-1):
        '''
        Test if gzip file contains more than the desired number of lines. 
        Returns True/False
        '''
        print("validate file length")
        if not self.validate_is_nonempty_file(file_path, min_file_size=1):
            return False
        else:
            with open(file_path, 'rb') as f:
                line=0
                file_right_num_lines = False
                for lines in f:
                    line=line+1
                    if line >= min_num_lines:
                        file_right_num_lines = True
                        break
            return file_right_num_lines

    def check_species(self):
        # check if species matches other
        for key in self.dict_arguments:
            if key == "species":
                species = self.dict_arguments[key]
                if species == "other":
                    # if species is other turn off pointfinder
                    for key in self.dict_arguments:
                        if key == "run_pointfinder":
                            self.dict_arguments[key] = self.dict_arguments[key] = "0"
                            return self.dict_arguments

                else:
                    return self.dict_arguments

    def change_species_name_format(self):
        for key in self.dict_arguments:
            if key == "species":
                # change _ to " " in species name & update species name in the arguments
                self.dict_arguments[key] = self.dict_arguments[key].replace("_", " ")

    def is_directory_with_correct_file_format(self, input_dir):
        #allowed extensions
        #TODO theres more extensions
        allowed_file_extensions_fastq = ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
        allowed_file_extensions_fasta = [".faa", ".fasta", "fasta.gz", "faa.gz"]
        #check if dir exists
        if os.path.isdir(input_dir):
            input_dir_to_path = Path(input_dir)
            folder = os.listdir(input_dir)
            fastq_count = 0
            fasta_count = 0
            fasta_bool = False
            fastq_bool = False
            for filename in folder:
                extension = "".join(pathlib.Path(filename).suffixes)
                if extension in allowed_file_extensions_fastq:
                    #check if there is at least one fasta or at least 2 fastq files?
                    fastq_count += 1
                    fastq_bool = True
                if extension in allowed_file_extensions_fasta:
                    fasta_count += 1
                    fasta_bool = True
            if fastq_count < 2 and fastq_bool == True:
                self.parser.error("Files in the input directory do not have a correct file format or there are not enough files. Please give a directory with files in the correct format. For fastq use: {}.".format(allowed_file_extensions_fastq))   
            elif fasta_count < 1 and fasta_bool == True:
                self.parser.error("Files in the input directory do not have a correct file format or there are not enough files. Please give a directory with files in the correct format. For fasta use: {}.".format(allowed_file_extensions_fasta))   

        else:
            print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
            sys.exit(1)      
        return input_dir_to_path

    def get_input_files_from_input_directory(self):
        self.input_files_r1 = {}
        self.input_files_r2 = {}
        self.input_files_fasta = {}
        fasta_ext = [".faa", ".fasta"]
        fastq_ext = ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
        self.isFastq = False
        #Vraagteken bij de R weggehaald?
        fq_pattern = re.compile("(.*?)(?:_S\d+_|_S\d+.|_|\.)(?:p)?R(1|2)(?:_.*\.|\..*\.|\.)f(ast)?q(\.gz)?")
        #TODO is this fasta pattern correct?
        fa_pattern = re.compile("(.*?)(?:_S\d+_|_S\d+.|_|\.)?(?:_.*\.|\..*\.|\.)f(ast)?(a|q)(\.gz)?")
        # Get the filenames that are used as input for resfinder, only filenames with pR1 and pR2 will be used.
        for key in self.dict_arguments:
            if key == "input_dir":
                directory_name_str = str(self.dict_arguments[key])
                input_directory = os.listdir(self.dict_arguments[key])
                
                for filename in input_directory:
                    ext = "".join(pathlib.Path(filename).suffixes)
                    match_fq = fq_pattern.fullmatch(filename)
                    match_fa = fa_pattern.fullmatch(filename)

                    #if the extension is fasta
                    if ext in fasta_ext:
                        # set the boolean
                        self.isFastq = False
                        if match_fa:
                            for filename in input_directory:
                                sample = match_fa.group(1)
                                self.input_files_fasta.update({sample: directory_name_str + "/" + filename})
                      
                    #if the extension is fastq
                    elif ext in fastq_ext:
                        self.isFastq = True
                        if match_fq:
                            sample = match_fq.group(1)
                            rtype = match_fq.group(2)
                            if rtype == "1":
                                self.input_files_r1.update({sample: directory_name_str + "/" + filename})
                            elif rtype == "2":
                                self.input_files_r2.update({sample: directory_name_str + "/" + filename})

    def create_yaml_file(self):
        yaml_setup_fq = open("config/setup_config_fq.yaml")
        yaml_setup_fa = open("config/setup_config_fa.yaml")
        
        #print(self.dict_arguments)
        #change path to str for yaml 
        for key in self.dict_arguments:
            if key == "input_dir":
                self.dict_arguments[key] = str(self.dict_arguments[key])
        #change yaml layout with received arguments & input
        with open("config/user_parameters.yaml", "w") as file:
            yaml = YAML()
            
            #if fastq
            if self.isFastq is True:
                config = yaml.load(yaml_setup_fq)
                # Add additional information to the dictionary
                self.dict_arguments['input_isfastq_boolean'] = self.isFastq
                
                # add filenames and parameters
                config['Parameters'] = self.dict_arguments
                config['samples_fastq_r1'] = self.input_files_r1
                config['samples_fastq_r2'] = self.input_files_r2
                
                #add to yaml
                yaml.dump(config, file)

            #if fasta
            elif self.isFastq is False:
                config = yaml.load(yaml_setup_fa)
                self.dict_arguments['input_isfastq_boolean'] = self.isFastq
                config['Parameters'] = self.dict_arguments
                config['samples_fasta'] = self.input_files_fasta
                yaml.dump(config, file)

    def run_snakemake_api(self):
        open_config_parameters = open("config/database_config.yaml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        cores = parsed_config['db-cores']

        open_config_parameters = open("config/user_parameters.yaml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        self.output_file_path = parsed_config['Parameters']['output_dir']
        self.queue = parsed_config['Parameters']['queue']
        
        if self.dict_arguments["dryrun"] is False:
            snakemake.snakemake(
                "Snakefile",
                use_conda = True,
                latency_wait = 60,
                cores = cores,
                nodes = cores,
                keepgoing = True,
                conda_frontend='mamba',
                cluster =f"bsub -q {self.queue} -W 60 -n {{threads}} -o {self.output_file_path}/log/cluster/{{name}}_{{wildcards}}_{{jobid}}.out -e {self.output_file_path}/log/cluster/{{name}}_{{wildcards}}_{{jobid}}.err -M {{resources.mem_mb}}M"
            )

        elif self.dict_arguments["dryrun"] is True:
            print("running with dryrun option")
            snakemake.snakemake(
                "Snakefile",
                use_conda = True,
                dryrun = True,
                latency_wait = 60,
                cores = cores,
                nodes = cores,
                keepgoing = True,
                conda_frontend='mamba',
                cluster =f"bsub -q {self.queue} -W 60 -n {{threads}} -o {self.output_file_path}/log/cluster/{{name}}_{{wildcards}}_{{jobid}}.out -e {self.output_file_path}/log/cluster/{{name}}_{{wildcards}}_{{jobid}}.err -M {{resources.mem_mb}}M"
            )

def main():
    s = StartPipeline()
    s.get_species_names_from_pointfinder_db()
    user_arguments = s.get_user_arguments()
    s.download_databases()
    
    j = JunoAmrWrapper(user_arguments["input_dir"])
   # j.download_databases()
    j.start_juno_pipeline()
    #j.check_species()
    #j.change_species_name_format()
    #j.get_input_files_from_input_directory()
    #j.create_yaml_file()
    #j.run_snakemake_api()


if __name__ == '__main__':
    main()