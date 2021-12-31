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
import general_juno_pipeline
import download_dbs
import species_helper_functions
import collect_user_arguments

class JunoAmrRun:
    """Class with the arguments and specifications that are only for the Juno-amr pipeline but inherit from PipelineStartup and RunSnakemake"""

    def __init__(self,
                input_dir,
                output_dir,
                species,
                resfinder_min_coverage=0.6,
                resfinder_identity_threshold=0.8,
                db_dir = "/mnt/db/juno-amr",
                update=False,
                #TODO explain why this is 1 or 0 not True or False.
                run_pointfinder=1,
                dryrun=False,
                #TODO not used in juno-amr yet
                #cores=300,
                #local=False,
                queue="bio",
                unlock=False
                ):

        """Initiating Juno-typing pipeline"""


        # Pipeline attributes
        self.pipeline_info = {'pipeline_name': "Juno-amr",
                                'pipeline_version': "0.1"}
        self.snakefile = "Snakefile"
        self.sample_sheet = "config/sample_sheet.yaml"
        self.input_dir = pathlib.Path(input_dir)
        self.output_dir = pathlib.Path(output_dir)
        #TODO moet een lowercase underscore string zijn
        self.species = species
        self.db_dir=pathlib.Path(db_dir)
        self.resfinder_min_coverage=resfinder_min_coverage
        self.resfinder_identity_threshold= resfinder_identity_threshold
        self.run_pointfinder=run_pointfinder
        self.update = update
        self.workdir = pathlib.Path(__file__).parent.absolute()
        self.useconda = True
        #TODO not using singularity yet
        #self.usesingularity = False
        #self.singularityargs = ""
        self.user_parameters = pathlib.Path("config/user_parameters.yaml")
        #TODO no idea about this
        #self.extra_software_versions = pathlib.Path('config/extra_software_versions.yaml')
        #TODO why is there an extra output_dir?
        #self.output_dir = output_dir
        #TODO base juno?
        #self.restarttimes = 2       
        # Checking if the input_dir comes from the Juno-assembly pipeline 
        self.startup = self.start_pipeline()
        # Parse arguments specific from the user
        self.user_params = self.write_userparameters()
        
        # Download databases if necessary
        if not unlock and not dryrun:
            print("starting download dbs")
            self.download_databases()

        # Run snakemake
        general_juno_pipeline.RunSnakemake(pipeline_name = self.pipeline_info['pipeline_name'],
                                            pipeline_version = self.pipeline_info['pipeline_version'],
                                            sample_sheet = self.sample_sheet,
                                            output_dir = self.output_dir,
                                            workdir = self.workdir,
                                            snakefile = self.snakefile,
                                            #TODO zelfde als in init
                                            #cores = cores,
                                            #local = local,
                                            queue = queue,
                                            unlock = unlock,
                                            #TODO weet niet of dit bij base hoort
                                            #rerunincomplete = rerunincomplete,
                                            dryrun = dryrun,
                                            useconda = self.useconda
                                            #TODO geen singularity voor nu
                                            #usesingularity = self.usesingularity,
                                            #singularityargs = self.singularityargs,
                                            #TODO weet niet of dit bij base hoort
                                            #restarttimes = self.restarttimes
                                            )

    def download_databases(self):
        """Function to download software and databases necessary for running the Juno-amr pipeline"""
        self.db_dir.mkdir(parents = True, exist_ok = True)
        download_dbs.get_downloads_juno_amr(self.db_dir, 'bin', self.update)

    def start_pipeline(self):
        """Function to start the pipeline (some steps from PipelineStartup need to be modified for the Juno-typing pipeline to accept fastq and fasta input"""
        print("start the pipelineee")
        #TODO do we always force towards one type of input?
        startup = general_juno_pipeline.PipelineStartup(self.input_dir, input_type = 'fastq')
        with open(self.sample_sheet, 'w') as file:
            yaml.dump(startup.sample_dict, file, default_flow_style=False)
        return startup

    def write_userparameters(self):

        config_params = {'input_dir': str(self.input_dir),
                        'output_dir': str(self.output_dir),
                        'species': str(self.species),
                        'run_pointfinder': str(self.run_pointfinder),
                        'resfinder_min_coverage': self.resfinder_min_coverage,
                        'resfinder_identity_threshold': self.resfinder_identity_threshold,
                        #TODO its ugly that this is hardcoded
                        'resfinder_db': str(self.db_dir.joinpath('resfinderdb')),
                        'pointfinder_db': str(self.db_dir.joinpath('pointfinderdb'))}
                        
        with open(self.user_parameters, 'w') as file:
            yaml.dump(config_params, file, default_flow_style=False)

        return config_params

    
if __name__ == '__main__':
    args = collect_user_arguments.collect_arguments()
    JunoAmrRun(input_dir = args.input_dir, 
                    output_dir = args.output_dir, 
                    species=args.species,
                    run_pointfinder=args.run_pointfinder,
                    db_dir = args.db_dir,
                    resfinder_min_coverage = args.resfinder_min_coverage,
                    resfinder_identity_threshold = args.resfinder_identity_threshold,
                    #cores = args.cores,
                    #local = args.local,
                    queue = args.queue,
                    #unlock = args.unlock,
                    #rerunincomplete = args.rerunincomplete,
                    dryrun = args.dry_run,
                    update = args.db_update)