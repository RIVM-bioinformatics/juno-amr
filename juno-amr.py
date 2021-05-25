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
#from cge.pointfinder import PointFinder

class JunoAmrWrapper:
    def __init__(self, arguments=None):
        """constructor, containing all variables"""

    #def get_species_from_resfinder(self):
        #point_dbs = PointFinder.get_db_names(db_path_point)
        #print(point_dbs)
        #species_file = open(self.resfinder_species_file)
        # species_data = species_file.readlines()

        # species_dict_lines = []
        # for line in species_data:
        #     if "species_transl" in line: 
        #         species_dict_lines.append(line)
        
        #species_transl
        #Deze dictionary uit de file halen en de values gebruiken als de choices. Values in een list stoppen
        # File openen
        # lezen tot file begint met de naam van de variabele?
        # dan lines selecteren tot de line een } heeft?
        # voor iedere line splitten op :?
        # het stukje achter de dubbele punt gebruiken maar de spatie replacen met _ voor de command line

    def get_user_arguments(self):
        """Function to parse the command line arguments from the user"""
        # Create argparser
        #TODO do we want custom error messages?
        self.parser = argparse.ArgumentParser(
            usage= "python3 juno-amr.py -s [species]  -i [directory with fastq files]",
            description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
            add_help = True
        )
        #TODO option 1: subparsers
        #TODO option 2: search for another argparse
        #TODO sys.argv if else eromheen bouwen
        # self.subparsers = self.parser.add_subparsers(help='sub-command help')
        # species_parser = self.subparsers.add_parser('species', help='blep')
        
        # species_parser.add_argument(
        #     '-s',
        #     '--species',
        #     help = "blaaaa",
        #     type=str)

        #TODO check if the given path is a path/directory
        # Add arguments
        self.parser.add_argument(
            "-o",
            "--output",
            type=str,
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
            type=self.is_directory_with_correct_files_fastq,
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
            help = "Full scientific name of the species sample, use underscores not spaces. Example: campylobacter_spp. Options to choose from: other, campylobacter_spp, campylobacter_jejuni, campylobacter_coli, escherichia_coli, salmonella_spp, plasmodium_falciparum, neisseria_gonorrhoeae, mycobacterium_tuberculosis, enterococcus_faecalis, enterococcus_faecium, klebsiella, helicobacter_pylori & staphylococcus_aureus",
            choices = ["other", "campylobacter_spp", "campylobacter_jejuni", "campylobacter_coli", "escherichia_coli", "salmonella_spp", "plasmodium_falciparum", "neisseria_gonorrhoeae", "mycobacterium_tuberculosis", "enterococcus_faecalis", "enterococcus_faecium", "klebsiella", "helicobacter_pylori", "staphylococcus_aureus"]
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
        #print(self.dict_arguments)

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
        print(self.dict_arguments)

    def is_directory_with_correct_files_fastq(self, input_dir):
        #allowed extensions
        allowed_file_extensions = ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
        #check if dir exists
        if os.path.isdir(input_dir):
            folder = os.listdir(input_dir)

            # for each file check if the file has the correct extension
            for filename in folder:
                extension = "".join(pathlib.Path(filename).suffixes)
                if extension not in allowed_file_extensions:
                    self.parser.error("Files in the input directory do not have a correct file format. Please give a directory with files in the format: {}".format(allowed_file_extensions))   
                return input_dir
            else:
                print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
                sys.exit(1)

    #TODO this function is not being used yet
    def is_directory_with_correct_files_fasta(self, input_dir):
        """Function to check if the given directory is a directory. Also checks if the files in the directory have the correct file format"""
        #allowed extensions
        allowed_file_extensions = [".faa", ".fasta"]
        #check if directory exists
        if os.path.isdir(input_dir):
            #Check the filename extension
            #simplify folder?
            folder = os.listdir(input_dir)
            for filename in folder:
                extension ="".join(pathlib.Path(filename).suffixes)
                if extension not in allowed_file_extensions:
                    self.parser.error("Files in the input directory do not have a correct file format. Please give a directory with files in the format: {}".format(allowed_file_extensions))
            return input_dir
        else:
            print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
            sys.exit(1)

    #TODO this function is not being used yet
    def get_input_files_from_input_directory_fasta(self):
        self.input_files = {}
        # get directory location
        for key in self.dict_arguments:
            if key == "input_dir":
                directory_name = self.dict_arguments[key]
                input_directory = os.listdir(self.dict_arguments[key])
                # put file name in self.input_files
                for filename in input_directory:
                    samplename = os.path.splitext(filename)[0]
                    # get the folder in front of the file name
                    self.input_files.update({samplename: directory_name + "/" + filename})

    def get_input_files_from_input_directory_fastq(self):
        self.input_files_r1 = {}
        self.input_files_r2 = {}
        fq_pattern = re.compile("(.*?)(?:_S\d+_|_S\d+.|_|\.)(?:p)?R?(1|2)(?:_.*\.|\..*\.|\.)f(ast)?q(\.gz)?")
        # Get the filenames that are used as input for resfinder, only filenames with pR1 and pR2 will be used.
        #TODO change this if we want others to use the pipeline as well or tell them to change the input names of their files
        for key in self.dict_arguments:
            if key == "input_dir":
                directory_name = self.dict_arguments[key]
                input_directory = os.listdir(self.dict_arguments[key])
                for filename in input_directory:
                    # TODO if the input dir ends with a "/" then the config will get double "//" in the name
                    match = fq_pattern.fullmatch(filename)
                    if match:
                        samplename = re.split("_pR(1|2)", filename)
                        if "1" in samplename[1]:
                            self.input_files_r1.update({samplename[0]: directory_name + "/" + filename})
                        elif "2" in samplename[1]:
                            self.input_files_r2.update({samplename[0]: directory_name + "/" + filename})

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

    #TODO this function is not being used yet
    def create_yaml_file_fasta(self):
        # Make config dir if this does not exist:
        Path("config").mkdir(parents=True, exist_ok=True)
        # # Make a yaml file, add arguments to the yaml file
        print("Producing yaml file for snakemake")
        
        # yaml lay-out
        # TODO make this into a file and load the file instead of inp
        inp = """
        #single fasta
        samples_fasta:
        \n       
        # parameters for pipeline given by user
        Parameters:
        """
        
        #change yaml layout with received arguments & input
        with open("config/config.yml", "w") as file:
            yaml = YAML()
            config = yaml.load(inp)
            # add parameters
            config['Parameters'] = self.dict_arguments
            # add filenames
            config['samples_fasta'] = self.input_files
            yaml.dump(config, file)

    def create_yaml_file_fastq(self):
        print("Producing yaml file for snakemake")
        yaml_setup = open("config/setup_config.yml")
        
        #change yaml layout with received arguments & input
        with open("config/user_parameters.yml", "w") as file:
            yaml = YAML()
            config = yaml.load(yaml_setup)
            # add parameters
            config['Parameters'] = self.dict_arguments
            # add filenames
            config['samples_fastq_r1'] = self.input_files_r1
            config['samples_fastq_r2'] = self.input_files_r2
            yaml.dump(config, file)

    def run_snakemake_api(self):
        open_config_parameters = open("config/database_config.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        cores = parsed_config['db-cores']

        open_config_parameters = open("config/user_parameters.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        output_dir_name = parsed_config['Parameters']['output_dir']
        current_path = os.path.abspath(os.getcwd())
        self.output_file_path = f"{output_dir_name}"

        if self.dict_arguments["dryrun"] is False:
            snakemake.snakemake(
                "Snakefile",
                use_conda = True,
                latency_wait = 5,
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
                latency_wait = 5,
                cores = cores,
                drmaa =f"-q bio -n {{threads}} -o {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.out -e {self.output_file_path}/log/drmaa/{{name}}_{{wildcards}}_{{jobid}}.err -R \"span[hosts=1]\" -R \"rusage[mem={{resources.mem_mb}}]\"",
                drmaa_log_dir = f"{self.output_file_path}/log/drmaa"
            )

    def run_snakemake_command(self):
        #TODO convert os system command to snakemake api
        #TODO if a run crashes or is stopped the directory will be locked, do we need to build in a --unlock command?
        open_config_parameters = open("config/database_config.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        cores = parsed_config['db-cores']
        #os.system("snakemake --snakefile Snakefile --cores 1 --use-conda")

        #get output dir name from other yaml file
        open_config_parameters = open("config/user_parameters.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        output_dir_name = parsed_config['Parameters']['output_dir']
        current_path = os.path.abspath(os.getcwd())
        self.output_file_path = f"{output_dir_name}"
        
        if self.dict_arguments["dryrun"] is False:
            os.system("snakemake --snakefile Snakefile --use-conda  --latency-wait 5 --cores %d --drmaa \" -q bio -n {threads} -o %s/log/drmaa/{name}_{wildcards}_{jobid}.out -e %s/log/drmaa/{name}_{wildcards}_{jobid}.err -R \"span[hosts=1]\" -R \"rusage[mem={resources.mem_mb}]\" \" --drmaa-log-dir %s/log/drmaa" % (cores, self.output_file_path, self.output_file_path, self.output_file_path))
        else:
            print("running dry run")
            os.system("snakemake --dryrun --snakefile Snakefile --use-conda --latency-wait 5 --cores %d --drmaa \" -q bio -n {threads} -o %s/log/drmaa/{name}_{wildcards}_{jobid}.out -e %s/log/drmaa/{name}_{wildcards}_{jobid}.err -R \"span[hosts=1]\" -R \"rusage[mem={resources.mem_mb}]\" \" --drmaa-log-dir %s/log/drmaa" % (cores, self.output_file_path, self.output_file_path, self.output_file_path))

def main():
    j = JunoAmrWrapper()
    #j.get_species_from_resfinder
    j.get_user_arguments()
    j.check_species()
    j.change_species_name_format()
    j.get_input_files_from_input_directory_fastq()
    j.create_yaml_file_fastq()
    j.run_snakemake_api()
    #j.run_snakemake_command()
    #j.preproccesing_for_summary_files()
    #j.pointfinder_result_summary()
   # j.pointfinder_prediction_summary()

if __name__ == '__main__':
    main()