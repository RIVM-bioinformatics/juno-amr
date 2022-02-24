"""
Juno-amr
Authors: Roxanne Wolthuis, Alejandra Hernandez Segura, Maaike van den Beld
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

from base_juno_pipeline import *
import sys
import yaml
import pathlib

sys.path.insert(0, 'bin/python_scripts/')
import download_dbs
from collect_user_arguments import CollectUserArguments

class JunoAmrRun(base_juno_pipeline.PipelineStartup,
                base_juno_pipeline.RunSnakemake):
    """Class with the arguments and specifications that are only for the Juno-amr pipeline but inherit from PipelineStartup and RunSnakemake"""

    def __init__(self,
                input_dir,
                output_dir,
                species,
                resfinder_min_coverage=0.6,
                resfinder_identity_threshold=0.8,
                db_dir = "/mnt/db/juno-amr",
                update=False,
                rerunincomplete=False,
                # This has to be 0 or 1, because True and False does not work with the shell command.
                run_pointfinder="1",
                dryrun=False,
                cores=300,
                local=False,
                queue="bio",
                unlock=False,
                **kwargs):

        """Initiating Juno-amr pipeline"""
        
        # Process arguments needed for base_juno classes
        output_dir = pathlib.Path(output_dir).resolve()
        workdir = pathlib.Path(__file__).parent.resolve()
        self.db_dir = pathlib.Path(db_dir).resolve()
        self.path_to_audit = output_dir.joinpath('audit_trail')
        
        # Initiate base_juno classes

        base_juno_pipeline.PipelineStartup.__init__(self,
            input_dir=pathlib.Path(input_dir).resolve(), 
            input_type='both',
            min_num_lines=1)
        base_juno_pipeline.RunSnakemake.__init__(self,
            pipeline_name='Juno-amr',
            pipeline_version='0.2',
            output_dir=output_dir,
            workdir=workdir,
            cores=cores,
            local=local,
            queue=queue,
            unlock=unlock,
            rerunincomplete=rerunincomplete,
            dryrun=dryrun,
            restarttimes=2,
            latency_wait=60,
            name_snakemake_report=str(self.path_to_audit.joinpath('juno_amr_report.html')),
            **kwargs)

        # Specific Juno-AMR pipeline attributes
        self.species = species
        self.resfinder_min_coverage = resfinder_min_coverage
        self.resfinder_identity_threshold = resfinder_identity_threshold
        self.run_pointfinder=run_pointfinder
        self.update = update
        self.workdir = pathlib.Path(__file__).parent.absolute()
        self.useconda = True
        self.user_parameters = pathlib.Path("config/user_parameters.yaml")
        self.restarttimes = 2      
        # Start pipeline  
        self.run_juno_amr_pipeline()

    def download_databases(self):
        """Function to download software and databases necessary for running the Juno-amr pipeline"""
        self.db_dir.mkdir(parents = True, exist_ok = True)
        download_dbs.get_downloads_juno_amr(self.db_dir, 'bin', self.update)

    def start_pipeline(self):
        """Function to start the pipeline (some steps from PipelineStartup need to be modified for the Juno-typing pipeline to accept fastq and fasta input"""
        self.start_juno_pipeline()
        with open(self.sample_sheet, 'w') as file:
            yaml.dump(self.sample_dict, file, default_flow_style=False)

    def write_userparameters(self):
        config_params = {'input_dir': str(self.input_dir),
                        'output_dir': str(self.output_dir),
                        'species': str(self.species),
                        'run_pointfinder': str(self.run_pointfinder),
                        'resfinder_min_coverage': self.resfinder_min_coverage,
                        'resfinder_identity_threshold': self.resfinder_identity_threshold,
                        'resfinder_db': str(self.db_dir.joinpath('resfinderdb')),
                        'pointfinder_db': str(self.db_dir.joinpath('pointfinderdb'))}
                        
        with open(self.user_parameters, 'w') as file:
            yaml.dump(config_params, file, default_flow_style=False)

        return config_params

    def run_juno_amr_pipeline(self):
        self.startup = self.start_pipeline()
        # Parse arguments specific from the user
        self.user_params = self.write_userparameters()
        # Download databases if necessary
        if not self.unlock and not self.dryrun:
            self.download_databases()
        self.successful_run = self.run_snakemake()
        assert self.successful_run, f'Please check the log files'
        if not self.dryrun or self.unlock:
            self.make_snakemake_report()

    
if __name__ == '__main__':
    c = CollectUserArguments()
    args = c.collect_arguments()
    JunoAmrRun(input_dir = args.input_dir, 
                    output_dir = args.output_dir, 
                    species=args.species,
                    run_pointfinder=args.run_pointfinder,
                    db_dir = args.db_dir,
                    resfinder_min_coverage = args.resfinder_min_coverage,
                    resfinder_identity_threshold = args.resfinder_identity_threshold,
                    cores = args.cores,
                    local = args.local,
                    queue = args.queue,
                    unlock = args.unlock,
                    rerunincomplete = args.rerunincomplete,
                    dryrun = args.dry_run,
                    update = args.db_update,
                    **args.snakemake_args)