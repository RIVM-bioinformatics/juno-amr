import pathlib
import sys
import argparse

sys.path.insert(0, 'bin/python_scripts/')
import species_helper_functions


def collect_species_options_from_db():
    species_options = species_helper_functions.get_species_names_from_pointfinder_db("/mnt/db/juno-amr/pointfinderdb")
    return species_options

def check_species(species, species_options):
    if species not in species_options:
        print(f"Incorrect species, please provide a species from this list: {species_options}")
    else:
        print("Valid species, continue pipeline")

def collect_arguments():
        #TODO add the -s-h help input from juno-amr here for a specific help on the species
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
            #TODO check the species type
            type = str,
            required = True,
            metavar="STR",
            dest="species",
            #space does not work on commandline, reason why the names are with underscore
            help = "Full scientific name of the species sample, use underscores not spaces. If the species that you are looking for is not available choose 'other'. Options:",
            #choices = species_options
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
            "-u",
            "--update",
            action='store_true',
            dest="db_update",
            help="Force database update even if they are present."
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
        #TODO: Get from ${irods_runsheet_sys__runsheet__lsf_queue} if it exists
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
        #TODO find out if I need this
        # parser.add_argument(
        #     "-l",
        #     "--local",
        #     action='store_true',
        #     help="Running pipeline locally (instead of in a computer cluster). Default is running it in a cluster."
        # )
        # Snakemake arguments
        #TODO figure out if I need this
        # parser.add_argument(
        #     "-u",
        #     "--unlock",
        #     action = 'store_true',
        #     help = "Unlock output directory (passed to snakemake)."
        # )
        #TODO figure out if I need this
        # parser.add_argument(
        #     "--rerunincomplete",
        #     action='store_true',
        #     help="Re-run jobs if they are marked as incomplete (passed to snakemake)."
        # )
        #TODO find out if I need this
        # parser.add_argument(
        #     "-c",
        #     "--cores",
        #     type = int,
        #     metavar = "INT",
        #     default = 300,
        #     help="Number of cores to use. Default is 300"
        # )
        raw_args = parser.parse_args()
        #modify species
        args = species_helper_functions.change_species_name_format(raw_args)
        return args