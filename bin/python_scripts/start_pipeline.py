import sys
from pathlib import Path
import os
import argparse
import pathlib

sys.path.insert(0, 'bin/python_scripts/')
from download_dbs import *

class StartPipeline:
    def __init__(self):
        """constructor, containing all variables"""
        self.path_to_pointfinder_db = "/mnt/db/juno-amr/pointfinderdb"

    def get_species_names_from_pointfinder_db(self):
        print("starting to collect species from pointfinder")
        self.species_options = []

        # If de database directory exists
        if Path(self.path_to_pointfinder_db).is_dir():
            print("Database present, collect species from database")
            for entry in os.scandir(self.path_to_pointfinder_db):
                if not entry.name.startswith('.') and entry.is_dir():
                    self.species_options.append(entry.name)
        
        else:
            print("No database found, using local file to collect species")
            #TODO hardcoded path
            with open("files/pointfinder_species.txt") as f:
                self.species_options = f.readlines()
                self.species_options = [species.strip() for species in self.species_options]

        self.species_options.append("other")
        return self.species_options

    def get_user_arguments(self):
        print("starting to parse all user arguments")
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

            self.parser.add_argument(
                "-i",
                "--input",
                type=pathlib.Path,
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
                default="/mnt/db/juno-amr/pointfinderdb",
                dest="pointfinder_db",
                help="Alternative database for pointfinder"
            )

            self.parser.add_argument(
                "-db_res",
                type=str,
                metavar="dir",
                default="/mnt/db/juno-amr/resfinderdb",
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

            self.parser.add_argument(
                "-q",
                "--queue",
                type=str,
                required=False,
                default="bio",
                dest="queue",
                help="Queue used if running in a cluster"
            )

            # parse arguments
            self.dict_arguments = vars(self.parser.parse_args())
            #set pathlib.path as string for yaml, yaml doesnt want a posixpath
            self.dict_arguments["output_dir"] = str(self.dict_arguments.get("output_dir"))
            return self.dict_arguments

    def download_databases(self):
        """Function to download software and databases necessary for running the Juno-amr pipeline"""
        db_dir = "/mnt/db/juno-amr"
        self.db_dir = pathlib.Path(db_dir)
        self.db_dir.mkdir(parents = True, exist_ok = True)
        self.update = self.dict_arguments["db_update"]
        d = DownloadDatabases()
        d.get_downloads_juno_amr(self.db_dir, 'bin', self.update)

def main():
    s = StartPipeline()
    s.get_species_names_from_pointfinder_db()
    user_arguments = s.get_user_arguments()
    s.download_databases()

if __name__ == '__main__':
    main()