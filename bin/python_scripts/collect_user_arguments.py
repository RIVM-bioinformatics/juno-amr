from base_juno_pipeline import helper_functions
import pathlib
import sys
import argparse
import os

class SpeciesHelpers:
    '''Class with helper functions for checking the input species for the PointFinder tool'''

    def get_species_names_from_pointfinder_db(self, path_to_pointfinder_db, path_to_species_file):
        '''
        Function to collect available species from PointFinder
        '''
        species_options = []
        if pathlib.Path(path_to_pointfinder_db).is_dir():
            print("Database present, collect species from database")
            for entry in os.scandir(path_to_pointfinder_db):
                if not entry.name.startswith('.') and entry.is_dir():
                    species_options.append(entry.name)    
        else:
            print("No database found, using local file to collect species")
            with open(path_to_species_file) as f:
                species_options = f.readlines()
                species_options = [species.strip() for species in species_options]

        species_options.append("other")
        return species_options

    def set_pointfinder_boolean(self, argument_dict):
        '''
        Decide if pointfinder has to be run based on the given species.
        '''
        if argument_dict.species == "other":
            argument_dict.run_pointfinder = "0"      
        return argument_dict



    def change_species_name_format(self, argument_dict):
        '''
        change _ to " " in species name & update species name in the arguments
        '''
        argument_dict.species = argument_dict.species.replace("_", " ")
        return argument_dict


class CollectUserArguments(SpeciesHelpers):

    def collect_arguments(self):
        #TODO hardcoded paths
        self.species_options = self.get_species_names_from_pointfinder_db("/mnt/db/juno-amr/pointfinderdb", "files/pointfinder_species.txt")
        
        #help specific for available species
        user_help_input = str(sys.argv[1])
        if user_help_input == "--species-help":
            print(f"Choose the full scientific name of the species sample, use underscores not spaces. Options: {self.species_options}. If you don't know the species choose 'other' as species option")
            sys.exit()
        else:
            parser = argparse.ArgumentParser(
                usage= "python3 juno-amr.py -s [species]  -i [directory with fastq files]",
                description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
                add_help = True
            )
            parser.add_argument(
                "-o",
                "--output",
                type=pathlib.Path,
                metavar="DIR",
                default="output",
                dest="output_dir",
                help="Relative or absolute path to the output directory. If non is given, an 'output' directory will be created in the current directory."
            )
            parser.add_argument(
                "-i",
                "--input",
                type = pathlib.Path,
                required = True,
                metavar = "DIR",
                dest="input_dir",
                help = "Relative or absolute path to the input directory. It must either be the output directory of the Juno-assembly pipeline or it must contain all the raw reads (fastq) and assemblies (fasta) files for all samples to be processed."
            )
            parser.add_argument(
                "-s",
                "--species",
                type = str.lower,
                required = True,
                metavar="STR",
                dest="species",
                #space does not work on commandline, reason why the names are with underscore
                help = f"Full scientific name of the species sample, use underscores not spaces. If the species that you are looking for is not available choose 'other'. Options:{self.species_options}",
                choices = self.species_options
            )
            parser.add_argument(
                "--resfinder_min_coverage",
                type=float,
                metavar="NUM",
                default=0.6,
                dest="resfinder_min_coverage",
                help="Minimum coverage to be used for ResFinder. It accepts values from 0-1. Default is 0.6.",
            )
            parser.add_argument(
                "--resfinder_identity_threshold",
                type=float,
                metavar="NUM",
                default=0.8,
                dest="resfinder_identity_threshold",
                help="Identity threshold to be used for ResFinder. It accepts values from 0-1. Default is 0.85",
            )
            parser.add_argument(
                "-d",
                "--db_dir",
                type=pathlib.Path,
                required=False,
                metavar="DIR",
                default="/mnt/db/juno-amr",
                dest="db_dir",
                help="Relative or absolute path to the directory that contains the databases for all the tools used in this pipeline or where they should be downloaded. Default is: /mnt/db/juno-amr",
            )
            parser.add_argument(
                "--update",
                action='store_true',
                dest="db_update",
                help="Force database update even if the databases are present."
            )
            parser.add_argument(
                "--run_pointfinder",
                type=str,
                default="1",
                metavar="STR",
                dest="run_pointfinder",
                #TODO explain why this is 0 and 1 not True and False
                help="Type one to run pointfinder, type 0 to not run pointfinder, default is 1."
            )
            parser.add_argument(
                "-n",
                "--dryrun",
                action='store_true',
                dest="dry_run",
                help="Dry run printing steps to be taken in the pipeline without actually running it (passed to snakemake)."
            )
            parser.add_argument(
                "-q",
                "--queue",
                type = str,
                required=False,
                default = 'bio',
                metavar = "STR",
                dest="queue",
                help = 'Name of the queue that the job will be submitted to if working on a cluster.'
            )
            parser.add_argument(
                "-l",
                "--local",
                action='store_true',
                help="Running pipeline locally (instead of in a computer cluster). Default is running it in a cluster."
            )
            # Snakemake arguments
            parser.add_argument(
                "-u",
                "--unlock",
                action = 'store_true',
                help = "Unlock output directory (passed to snakemake)."
            )
            parser.add_argument(
                "--rerunincomplete",
                action='store_true',
                help="Re-run jobs if they are marked as incomplete (passed to snakemake)."
            )
            parser.add_argument(
                "-c",
                "--cores",
                type = int,
                metavar = "INT",
                default = 300,
                help="Number of cores to use. Default is 300"
            )
            parser.add_argument(
                "--snakemake-args",
                nargs='*',
                default={},
                action=helper_functions.SnakemakeKwargsAction,
                help="Extra arguments to be passed to snakemake API (https://snakemake.readthedocs.io/en/stable/api_reference/snakemake.html)."
            )
            raw_args = parser.parse_args()
            modified_species_args = self.change_species_name_format(raw_args)
            final_args = self.set_pointfinder_boolean(modified_species_args)
        return final_args