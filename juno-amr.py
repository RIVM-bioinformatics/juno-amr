"""
Wrapper made in python for the juno-amr pipeline
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
        self.arguments = []

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
            type=self.is_directory_with_correct_files,
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
            # TODO Later replace underscore with space for resfinder input[put in between quotes?]
            #space does not work on commandline, reason why the names are with underscore
            help = "Full scientific name of the species sample, use underscores not spaces. Example: Campylobacter_spp. Options to choose from: Campylobacter_spp, Campylobacter_jejuni, Campylobacter_coli, Escherichia_coli, Salmonella_spp, Plasmodium_falciparum, Neisseria_gonorrhoeae, Mycobacterium_tuberculosis, Enterococcus_faecalis, Enterococcus_faecium, Klebsiella, Helicobacter_pylori & Staphylococcus_aureus",
            # TODO Currently with capital letter, remove or not?
            # TODO use nargs to take multiple arguments, so we can use a space in the text?, i think i prefer _ and replace it later..
            choices = ["Campylobacter_spp", "Campylobacter_jejuni", "Campylobacter_coli", "Escherichia_coli", "Salmonella_spp", "Plasmodium_falciparum", "Neisseria_gonorrhoeae", "Mycobacterium_tuberculosis", "Enterococcus_faecalis", "Enterococcus_faecium", "Klebsiella", "Helicobacter_pylori", "Staphylococcus_aureus"]
        )

        # Add coverage argument
        self.parser.add_argument(
            #TODO Default value?
            "-l",
            "--min_cov",
            type=float,
            required=True,
            metavar="",
            dest="coverage",
            help="Minimum coverage of ResFinder"
        )

        # Add identity threshold argument
        self.parser.add_argument(
            #TODO Default value?
            "-t",
            "--threshold",
            type=float,
            required=True,
            metavar="",
            dest="threshold",
            help="Threshold for identity of resfinder"
        )
        # TODO simplify this
        # parse arguments
        self.arguments = self.parser.parse_args()
        self.dict_arguments = vars(self.arguments)

    #Check if the given path is an directory
    def is_directory_with_correct_files(self, input_dir):
        # TODO Did not check inside the file, only if the file has the correct extension.. what if the content of the file is incorrect?
        """Function to check if the given directory is a directory. Also checks if the files in the directory have the correct file format"""
        #allowed extensions
        allowed_file_extensions = [".faa", ".fasta"]
        #check if directory exists
        if os.path.isdir(input_dir):
            #Check the filename extension
            folder = os.listdir(input_dir)
            for filename in folder:
                extension ="".join(pathlib.Path(filename).suffixes)
                if extension not in allowed_file_extensions:
                    self.parser.error("Files in the input directory do not have a correct file format. Please give a directory with files in the format: {}".format(allowed_file_extensions))
            return input_dir
        else:
            print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
            sys.exit(1)

    def get_input_files_from_input_directory(self):
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

    def create_yaml_file(self):
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

    def run_snakemake_command(self):
        #TODO get correct command to run snakemake
        pass
        

def main():
    j = JunoAmrWrapper()
    j.get_user_arguments()
    j.get_input_files_from_input_directory()
    j.create_yaml_file()

if __name__ == '__main__':
    main()