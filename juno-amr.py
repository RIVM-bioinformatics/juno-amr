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
import yaml
import pathlib
from pathlib import Path
from ruamel.yaml import YAML

class JunoAmrWrapper:
    def __init__(self, arguments=None):
        """constructor, containing all variables"""

    def get_user_arguments(self):
        """Function to parse the command line arguments from the user"""

        # Create argparser
        #TODO do we want custom error messages?
        self.parser = argparse.ArgumentParser(
            # TODO: place example of run here, how to make arguments positional/optional?
            usage= "amr_wrapper.py ....",
            # TODO: Add proper description of the tool
            description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
            add_help = True
        )

        #Add input directory argument
        self.parser.add_argument(
            "-i",
            "--input",
            type=self.is_directory_with_correct_files_fastq,
            required=True,
            metavar="",
            dest="input_dir",
            #TODO For now the only input accepted is a fasta file, need to decide on fasta or fastq
            help="Path to the directory of your input. Example: path/to/input/fasta or path/to/input/fastq"
        )

        # Add species argument
        self.parser.add_argument(
            "-s",
            "--species",
            type = str,
            required = True,
            metavar="",
            dest="species",
            #space does not work on commandline, reason why the names are with underscore
            help = "Full scientific name of the species sample, use underscores not spaces. Example: Campylobacter_spp. Options to choose from: other, Campylobacter_spp, Campylobacter_jejuni, Campylobacter_coli, Escherichia_coli, Salmonella_spp, Plasmodium_falciparum, Neisseria_gonorrhoeae, Mycobacterium_tuberculosis, Enterococcus_faecalis, Enterococcus_faecium, Klebsiella, Helicobacter_pylori & Staphylococcus_aureus",
            # TODO Currently with capital letter --> transform input to lowercase always
            choices = ["other", "Campylobacter_spp", "Campylobacter_jejuni", "Campylobacter_coli", "Escherichia_coli", "Salmonella_spp", "Plasmodium_falciparum", "Neisseria_gonorrhoeae", "Mycobacterium_tuberculosis", "Enterococcus_faecalis", "Enterococcus_faecium", "Klebsiella", "Helicobacter_pylori", "Staphylococcus_aureus"]
        )

        # Add coverage argument
        self.parser.add_argument(
            "-l",
            "--min_cov",
            type=float,
            metavar="",
            default=0.6,
            dest="coverage",
            help="Minimum coverage of ResFinder"
        )

        # Add identity threshold argument
        self.parser.add_argument(
            "-t",
            "--threshold",
            type=float,
            metavar="",
            default=0.8,
            dest="threshold",
            help="Threshold for identity of resfinder"
        )

        #Add pointfinder database argument
        self.parser.add_argument(
            "-db_point",
            type=str,
            metavar="",
            #TODO change hardcoded path
            #TODO check if valid path
            default="../../../db/resfinder/db_pointfinder",
            dest="pointfinder_db",
            help="Alternative database for pointfinder"
        )

        #Add resfinder database argument
        self.parser.add_argument(
            "-db_res",
            type=str,
            metavar="",
            #TODO change hardcoded path
            #TODO check if valid path
            default="../../../db/resfinder/db_resfinder",
            dest="resfinder_db",
            help="Alternative database for resfinder"
        )

        #Option to run pointfinder
        self.parser.add_argument(
            "--point",
            action = 'store_true',
            default=True,
            dest="run_pointfinder",
            help="To run pointfinder or not"
        )

        # parse arguments
        self.dict_arguments = vars(self.parser.parse_args())
        #print(self.dict_arguments)

    def check_species(self):
        # check if species matches other
        for key in self.dict_arguments:
            if key == "species":
                species = self.dict_arguments[key]
                print(species)
                if species == "other":
                    print("species is other")
                    print("Changing --point argument to false")
                    for key in self.dict_arguments:
                        if key == "run_pointfinder":
                            print("before: ", self.dict_arguments[key])
                            print(self.dict_arguments)
                            self.dict_arguments[key] = self.dict_arguments[key] = False
                            print("After: ", self.dict_arguments)
                            return self.dict_arguments

        #     print("Species unknown, resfinder will be executed, but pointfinder can not be run without a species.")
        #     print("continue pipeline")
        #     return species
                else:
                    print("species recognized and approved, continue pipeline")
                    # for key in self.dict_arguments:
                    #     if key == "run_pointfinder":
                    #         print("before: ", self.dict_arguments[key])
                    #         self.dict_arguments[key] = str(self.dict_arguments[key]).replace("True", "--point")
                    #         print("After: ", self.dict_arguments[key])
                    return self.dict_arguments
        #     return species
        # if so argument point should be changed to an empty string
        # else argument for point should be --point

    def change_species_name_format(self):
        for key in self.dict_arguments:
            if key == "species":
                # change _ to " " in species name & update species name in the arguments
                self.dict_arguments[key] = self.dict_arguments[key].replace("_", " ")
    
    def is_directory_with_correct_files_fastq(self, input_dir):
        #allowed extensions
        allowed_file_extensions = ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
        #check if dir exists
        if os.path.isdir(input_dir):
            folder = os.listdir(input_dir)
            for filename in folder:
                #get filename extension
                extension = "".join(pathlib.Path(filename).suffixes)
                if extension not in allowed_file_extensions:
                    self.parser.error("Files in the input directory do not have a correct file format. Please give a directory with files in the format: {}".format(allowed_file_extensions))   
                return input_dir
            else:
                print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
                sys.exit(1)

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
        for key in self.dict_arguments:
            if key == "input_dir":
                directory_name = self.dict_arguments[key]
                input_directory = os.listdir(self.dict_arguments[key])
                for filename in input_directory:
                    #get the sample name minus _r1/r2
                    # TODO only works with underscore, will this be the standard format?
                    # TODO if the input dir ends with a "/" then the config will get double "//" in the name
                    # TODO do we end with a slash or not?
                    samplename = os.path.splitext(filename)[0].split("_")
                    #print("samplename: ", samplename)
                    if "R1" in samplename[1]:
                        self.input_files_r1.update({samplename[0]: directory_name + "/" + filename})
                    elif "R2" in samplename[1]:
                        self.input_files_r2.update({samplename[0]: directory_name + "/" + filename})

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
        #open the yaml setup file
        #TODO change this layout for fasta or fastq
        yaml_setup = open("config/setup_config.yml")
        
        #change yaml layout with received arguments & input
        with open("config/user_parameters.yml", "w") as file:
            yaml = YAML()
            config = yaml.load(yaml_setup)
            # add parameters
            config['Parameters'] = self.dict_arguments
            # add filenames
            # TODO or change to fasta
            config['samples_fastq_r1'] = self.input_files_r1
            config['samples_fastq_r2'] = self.input_files_r2

            yaml.dump(config, file)

    def run_snakemake_command(self):
        # Run snakemake with resfinder
        open_config_parameters = open("config/database_config.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        #print("Config cores: ", parsed_config['local-cores'])
        memory = parsed_config['mem_mb']
        print("test", memory)
        #print("Starting to run snakemake")
        #os.system("snakemake --snakefile Snakefile --cores 1 --use-conda --drmaa"")
        print("testing to run on cluster")
        os.system("snakemake --snakefile Snakefile --use-conda --cores 8 --drmaa \" -q bio -n {threads} -o test/log/drmaa/test.out -e test/log/drmaa/test.err -R \"span[hosts=1]\" -R \"rusage[mem={resources.mem_mb}]\" \" --drmaa-log-dir test/log/drmaa")
        
def main():
    j = JunoAmrWrapper()
    j.get_user_arguments()
    j.check_species()
    j.change_species_name_format()
    #choose fasta or fastq
    #j.get_input_files_from_input_directory_fasta()
    j.get_input_files_from_input_directory_fastq()
    #j.create_yaml_file_fasta()
    j.create_yaml_file_fastq()
    j.run_snakemake_command()

if __name__ == '__main__':
    main()