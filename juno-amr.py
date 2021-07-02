"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

#imports
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
import download_dbs

class JunoAmrWrapper:
    def __init__(self, arguments=None):
        """constructor, containing all variables"""
        self.path_to_pointfinder_db = "/mnt/db/resfinder/db_pointfinder"

    def get_species_names_from_pointfinder_db(self):
        self.species_options = []
        for entry in os.scandir(self.path_to_pointfinder_db):
            if not entry.name.startswith('.') and entry.is_dir():
                self.species_options.append(entry.name)

        self.species_options.append("other")
        return self.species_options

    def get_user_arguments(self):
        """Function to parse the command line arguments from the user"""
        # Select 2 arguments in the case someone asks for help on the species
        user_help_input = str(sys.argv[1] + sys.argv[2])
        if user_help_input == "-s-h":
            #Give the help and exit the program
            print(f"Choose the full scientific name of the species sample, use underscores not spaces. Options: {self.species_options}. If you don't know the species choose 'other' as species option")
            sys.exit()
        else:
            # Create argparser
            self.parser = argparse.ArgumentParser(
                usage= "python3 juno-amr.py -s [species]  -i [directory with fastq files]",
                description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
                add_help = True
            )
          
            # Add arguments
            self.parser.add_argument(
                "-o",
                "--output",
                type=pathlib.Path,
                required=False,
                metavar="dir",
                default="output",
                dest="output_dir",
                help="Path to the directory you want to use as an output directory, if non is given the default will be an output directory in the Juno-amr folder"
            )

            #TODO decide on fasta or fastq
            self.parser.add_argument(
                "-i",
                "--input",
                type=self.is_directory_with_correct_file_format,
                required=True,
                metavar="dir",
                dest="input_dir",
                help="Path to the directory of your input. Example: path/to/input/fastq"
            )

            self.parser.add_argument(
                "-s",
                "--species",
                type = str.lower,
                required = True,
                metavar="str",
                dest="species",
                #space does not work on commandline, reason why the names are with underscore
                help = f"Full scientific name of the species sample, use underscores not spaces. Options: {self.species_options}",
                choices = self.species_options
            )

            self.parser.add_argument(
                "-l",
                "--min_cov",
                type=float,
                metavar="float",
                default=0.6,
                dest="coverage",
                help="Minimum coverage of ResFinder"
            )

            self.parser.add_argument(
                "-t",
                "--threshold",
                type=float,
                metavar="float",
                default=0.8,
                dest="threshold",
                help="Threshold for identity of resfinder"
            )

            self.parser.add_argument(
                "-db_point",
                type=str,
                metavar="dir",
                default="/mnt/db/resfinder/db_pointfinder",
                dest="pointfinder_db",
                help="Alternative database for pointfinder"
            )

            self.parser.add_argument(
                "-db_res",
                type=str,
                metavar="dir",
                default="/mnt/db/resfinder/db_resfinder",
                dest="resfinder_db",
                help="Alternative database for resfinder"
            )

            self.parser.add_argument(
                "-u",
                "--update",
                action='store_true',
                dest="db_update",
                help="Force database update even if they are present."
            )

            self.parser.add_argument(
                "--point",
                type=str,
                default="1",
                dest="run_pointfinder",
                metavar="",
                help="Type one to run pointfinder, type 0 to not run pointfinder, default is 1."
            )

            self.parser.add_argument(
                "-n",
                "--dryrun",
                action='store_true',
                dest="dryrun",
                help="If you want to run a dry run type --dryrun in your command"
            )

            # parse arguments
            self.dict_arguments = vars(self.parser.parse_args())
            #set pathlib.path as string for yaml, yaml doesnt want a posixpath
            self.dict_arguments["output_dir"] = str(self.dict_arguments.get("output_dir"))

    def download_databases(self):
        """Function to download software and databases necessary for running the Juno-amr pipeline"""
        db_dir = "mnt/db/juno-amr"
        self.db_dir = pathlib.Path(db_dir)
        self.db_dir.mkdir(parents = True, exist_ok = True)
        self.update = self.dict_arguments["db_update"]

        #print(self.db_dir, 'bin', self.update)
        download_dbs.get_downloads_juno_amr(self.db_dir, 'bin', self.update)

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

    #TODO this function is not being used yet
    def check_directory_format(self, given_path):
        if given_path.endswith("/"):
            print("path is correct:", given_path)
            return given_path
        else:
            print("path is incorrect format, changing format")
            correct_format = given_path + "/"
            print("format changed")
            return correct_format

    def is_directory_with_correct_file_format(self, input_dir):
        #allowed extensions
        #TODO theres more extensions
        allowed_file_extensions = ['.fastq', '.fq', '.fastq.gz', '.fq.gz', ".faa", ".fasta", "fasta.gz", "faa.gz"]
        #check if dir exists
        if os.path.isdir(input_dir):
            input_dir_to_path = Path(input_dir)
            folder = os.listdir(input_dir)
            # split de ext van folder[0]
            #for filename in folder, check of de extension gelijk is
            # for each file check if the file has the correct extension
            # TODO als er gemengde files zijn gaat het nog fout, iedere extension is nu goed, maar het kan maar 1 extension per dir zijn
            for filename in folder:
                extension = "".join(pathlib.Path(filename).suffixes)
                if extension not in allowed_file_extensions:
                    self.parser.error("Files in the input directory do not have a correct file format. Please give a directory with files in the format: {}".format(allowed_file_extensions))   
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
        
        print(self.dict_arguments)
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
        #Get cores from config
        open_config_parameters = open("config/database_config.yaml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        cores = parsed_config['db-cores']

        #Get output dir from other config
        open_config_parameters = open("config/user_parameters.yaml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        self.output_file_path = parsed_config['Parameters']['output_dir']
        
        #run snakemake API with or without dryrun
        if self.dict_arguments["dryrun"] is False:
            snakemake.snakemake(
                "Snakefile",
                use_conda = True,
                latency_wait = 30,
                cores = cores,
                drmaa =f"-q bio -n {{threads}} -o {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.out -e {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.err -R \"span[hosts=1]\" -R \"rusage[mem={{resources.mem_mb}}]\"",
                drmaa_log_dir = f"{self.output_file_path}/log/drmaa"
            )

        elif self.dict_arguments["dryrun"] is True:
            print("running with dryrun option")
            snakemake.snakemake(
                "Snakefile",
                use_conda = True,
                dryrun = True,
                latency_wait = 30,
                cores = cores,
                drmaa =f"-q bio -n {{threads}} -o {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.out -e {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.err -R \"span[hosts=1]\" -R \"rusage[mem={{resources.mem_mb}}]\"",
                drmaa_log_dir = f"{self.output_file_path}/log/drmaa"
            )

    #TODO this function is not being used yet
    def check_if_db_exists(self, db_path):
        #TODO only working for pointfinder, make working for resfinder later
        if os.path.isdir(db_path):
            print("found db directory, checking for files")
            if len(os.listdir("../../../db/resfinder/db_pointfinder")) == 0:
                print("No files found in directory, downloading latest pointfinder database")
                # TODO make a variable in a different file for this link
                os.system("git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git /mnt/db/resfinder/db_pointfinder")

            else:
                print("Database pointfinder found, proceed pipeline")
        else:
            print("did not find a database, clowning new db now")
            # todo make a variable in a different file for this link
            #TODO to make the database working need to run install.py to index the databases with KMA how to fix this?
            os.system("git clone https://git@bitbucket.org/genomicepidemiology/pointfinder_db.git /mnt/db/resfinder/db_pointfinder")


        
        #change yaml layout with received arguments & input
        with open("config/config.yaml", "w") as file:
            yaml = YAML()
            config = yaml.load(inp)
            # add parameters
            config['Parameters'] = self.dict_arguments
            # add filenames
            config['samples_fasta'] = self.input_files
            yaml.dump(config, file)

def main():
    j = JunoAmrWrapper()
    j.get_species_names_from_pointfinder_db()
    j.get_user_arguments()
    j.download_databases()
    #j.check_species()
    #j.change_species_name_format()
    #j.get_input_files_from_input_directory()
    #j.create_yaml_file()
    #j.run_snakemake_api()


if __name__ == '__main__':
    main()