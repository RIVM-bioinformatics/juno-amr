"""
Juno-amr
Authors: Roxanne Wolthuis, Alejandra Hernandez Segura, Maaike van den Beld
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

# Dependencies
import argparse
import subprocess
import yaml
from dataclasses import dataclass, field
from version import __package_name__, __version__, __description__
from pathlib import Path
from juno_library import Pipeline

#own scripts
import bin.downloads

def main() -> None:
    juno_amr = JunoAmr()
    juno_amr.run()

def get_species() -> list[str]:
    with open(
        Path(__file__).parent.joinpath("files", "pointfinder_species.txt"), mode="r"
    ) as f:
        species = [s.strip().lower() for s in f.readlines()]
        species.append("other")
        return species

@dataclass
class JunoAmr(Pipeline):
    pipeline_name: str = __package_name__
    pipeline_version: str = __version__
    input_type: str = "both"
    species: list[str] = field(default_factory=get_species)

    def _add_args_to_parser(self) -> None:
        super()._add_args_to_parser()
        species = self.species
        
        class HelpSpeciesAction(argparse.BooleanOptionalAction):
            def __call__(self, *args, **kwargs) -> None:  # type: ignore
                print("\n".join([f"The accepted species are:"] + species))
                exit(0)

        self.parser.description = "Juno-amr pipeline. Automated pipeline for bacterial AMR analysis."

        self.add_argument(
            "--help-species",
            action=HelpSpeciesAction,
            help="Prints the genera accepted by this pipeline.",
        )
        self.add_argument(
            "-s",
            "--species",
            type = str.lower,
            required = True,
            metavar="STR",
            help = f"Full scientific name of the species sample, use underscores not spaces. If the species that you are looking for is not available choose 'other'. Options:{self.species}",
            choices = self.species
        )
        self.add_argument(
            "-m",
            "--metadata",
            type=Path,
            default=None,
            metavar="FILE",
            dest="metadata_file",
            help="Relative or absolute path to a .csv file. If provided, it must contain at least one column with the 'Sample' name (name of the file but removing _R1.fastq.gz) and a column called 'Genus' (mind the capital in the first letter). The genus provided will be used to choose the reference genome to analyze de QC of the de novo assembly.",
        )
        self.add_argument(
            "--resfinder_min_coverage",
            type=float,
            metavar="NUM",
            default=0.6,
            help="Minimum coverage to be used for ResFinder. It accepts values from 0-1. Default is 0.6.",
        )
        self.add_argument(
            "--resfinder_identity_threshold",
            type=float,
            metavar="NUM",
            default=0.8,
            help="Identity threshold to be used for ResFinder. It accepts values from 0-1. Default is 0.85",
        )
        self.add_argument(
            "-d",
            "--db_dir",
            type=Path,
            required=False,
            metavar="DIR",
            default="/mnt/db/juno-amr",
            help="Relative or absolute path to the directory that contains the databases for all the tools used in this pipeline or where they should be downloaded. Default is: /mnt/db/juno-amr",
        )
        #TODO rename this specific or remove
        # self.add_argument(
        #     "--update",
        #     action='store_true',
        #     help="Force database update even if the databases are present."
        # )
        self.add_argument(
            "--run_pointfinder",
            type=bool,
            default=True,
            metavar="BOOL",
            help="Type one to run pointfinder, type False to not run pointfinder, default is True."
        )

    def _parse_args(self) -> argparse.Namespace:
        args = super()._parse_args()
        # Remove this if containers can be used with juno-amr
        if "--no-containers" not in self.argv:
            self.argv.append("--no-containers")

        args = super()._parse_args()
        self.db_dir: Path = args.db_dir.resolve()
        self.resfinder_min_coverage: float = args.resfinder_min_coverage
        self.resfinder_identity_threshold: float = args.resfinder_identity_threshold
        #TODO Keep or remove?
        # self.update: bool = args.update
        self.run_pointfinder: int = args.run_pointfinder
        self.species =args.species
        self.metadata_file: Path = args.metadata_file
        # self.update_dbs: bool = args.update
        return args
    
    def setup(self) -> None:
        super().setup()
        self.update_sample_dict_with_metadata()
        
        if self.snakemake_args["use_singularity"]:
            self.snakemake_args["singularity_args"] = " ".join(
                [
                    self.snakemake_args["singularity_args"],
                    f"--bind {self.db_dir}:{self.db_dir}",
                ]
            )

        #Check species to decide wether or not to run pointfinder
        if self.species == "other":
                self.run_pointfinder =False

        self.user_parameters = {
            "input_dir": str(self.input_dir),
            "out": str(self.output_dir),
            "exclusion_file": str(self.exclusion_file),
            "species": self.species,
            #TODO check juno-typing serotypefinder for specific treshold per tool line: 163
            "resfinder_min_coverage": self.resfinder_min_coverage,
            "resfinder_identity_threshold": self.resfinder_identity_threshold,
            "run_pointfinder": self.run_pointfinder,
            # "update": self.update,
            "run_in_container": self.snakemake_args["use_singularity"],
            "db_dir": str(self.db_dir),
            "resfinder_db": str(self.db_dir.joinpath("resfinder_db")),
            "pointfinder_db": str(self.db_dir.joinpath("pointfinder_db")),
            "virulencefinder_db": str(self.db_dir.joinpath("virulencefinderdb")),
        }
        with open(
            Path(__file__).parent.joinpath("config/pipeline_parameters.yaml")
        ) as f:
            parameters_dict = yaml.safe_load(f)
        self.snakemake_config.update(parameters_dict)

    def update_sample_dict_with_metadata(self) -> None:

        self.get_metadata_from_csv_file(
            filepath=self.metadata_file, expected_colnames=["sample", "full_species_name"]
        )
        for sample, properties in self.sample_dict.items():
            try:
                properties["species"] = (
                    self.juno_metadata[sample]["full_species_name"].strip().lower()
                )
            except (KeyError, TypeError, AttributeError):
                properties["species"] = self.genus  # type: ignore
        print(self.sample_dict)
    def run(self) -> None:
        self.setup()
        if not self.dryrun or self.unlock:
            self.path_to_audit.mkdir(parents=True, exist_ok=True)
            downloads_juno_amr = bin.downloads.DownloadsJunoAmr(
                self.db_dir,
                # update_dbs=self.update_dbs,
                software_resfinder_asked_version="e976708dc742d53dd0eb15422a4e7f2285518787",
                software_virulence_finder_asked_version="2.0.4",
            )
            self.downloads_versions = downloads_juno_amr.downloaded_versions
            with open(
                self.path_to_audit.joinpath("database_versions.yaml"), "w"
            ) as file_:
                yaml.dump(self.downloads_versions, file_, default_flow_style=False)

        if not self.dryrun or self.unlock:
            subprocess.run(
                [
                    "find",
                    self.output_dir,
                    "-type",
                    "f",
                    "-empty",
                    "-exec",
                    "rm",
                    "{}",
                    ";",
                ]
            )
            subprocess.run(
                [
                    "find",
                    self.output_dir,
                    "-type",
                    "d",
                    "-empty",
                    "-exec",
                    "rm",
                    "-rf",
                    "{}",
                    ";",
                ]
            )
        super().run()

if __name__ == "__main__":
    main()