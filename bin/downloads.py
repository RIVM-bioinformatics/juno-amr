"""
Juno-amr
Authors: Roxanne Wolthuis
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""
import argparse
import pathlib
import subprocess
import os
import juno_library.helper_functions as hf

class DownloadsJunoAmr:
    """Class that performs all necessary software and database downloads for
    the Juno Amr pipeline if necessary"""

    def __init__(
        self,
        db_dir,
        update_dbs=False,
        software_resfinder_asked_version="4.6.0",
        software_virulence_finder_asked_version="2.0.4",
        # By default the db is collected from the master branch, the commit hash currently in use is: #50925ea425763a7a43d62a0b974302bf1d52575b
        db_resfinder_asked_version="master", 
        #this is the only working branch of pointfinder at the moment
        db_pointfinder_asked_version="legacy_final_working_version",
        db_virulencefinder_asked_version="master"
        #Amrfinderplus db is manually downloaded, the current version in use is: 2022-12-19.1 

    ):
        self.db_dir = pathlib.Path(db_dir)
        self.bin_dir = pathlib.Path(__file__).parent.absolute()
        self.update_dbs = update_dbs
        self.downloaded_versions = self.get_downloads_juno_amr(
            software_virulence_finder_asked_version=software_virulence_finder_asked_version,
            software_resfinder_asked_version=software_resfinder_asked_version,
            db_resfinder_asked_version=db_resfinder_asked_version,
            db_pointfinder_asked_version=db_pointfinder_asked_version,
            db_virulencefinder_asked_version=db_virulencefinder_asked_version
        )

    def download_software_resfinder(self, version):
        """Function to download resfinder if it is not present"""
        current_dir = os.getcwd()
        resfinder_software_dir = self.bin_dir.joinpath("resfinder")
        if not resfinder_software_dir.joinpath("run_resfinder.py").is_file():
            print("\x1b[0;33m Downloading resfinder software...\n\033[0;0m")
            os.chdir(self.bin_dir)
            os.system(f"git clone https://bitbucket.org/genomicepidemiology/resfinder.git && cd {resfinder_software_dir} && git reset --hard {version}")
            os.chdir(current_dir)
        return version

    def download_software_virulencefinder(self, version):
        """Function to download virulencefinder if it is not present"""
        virulencefinder_software_dir = self.bin_dir.joinpath("virulencefinder")
        if not virulencefinder_software_dir.joinpath("virulencefinder.py").is_file():
            print("\x1b[0;33m Downloading virulencefinder software...\n\033[0;0m")
            hf.download_git_repo(
                version,
                "https://bitbucket.org/genomicepidemiology/virulencefinder.git",
                virulencefinder_software_dir
            )
        return version 
    
    def download_db_virulencefinder(self, version):
        """Function to download virulencefinder database if it is not present"""
        virulencefinder_db_dir = self.db_dir.joinpath("virulencefinderdb")
        if not virulencefinder_db_dir.joinpath("config").is_file():
            print("\x1b[0;33m Downloading virulencefinder database...\n\033[0;0m")
            hf.download_git_repo(
                version,
                "https://bitbucket.org/genomicepidemiology/virulencefinder_db.git",
                virulencefinder_db_dir
            )
        return version

    def download_db_resfinder(self, version):
        """Function to download resfinder database if it is not present"""
        resfinder_db_dir = self.db_dir.joinpath("resfinder_db")
        current_dir = os.getcwd()
        if not resfinder_db_dir.joinpath("config").is_file():
            print("\x1b[0;33m Downloading resfinder database...\n\033[0;0m")
            hf.download_git_repo(
                version,
                "https://bitbucket.org/genomicepidemiology/resfinder_db.git",
                resfinder_db_dir
            )
            os.chdir(resfinder_db_dir)
            os.system(f"python3 INSTALL.py")
            #Applying a change in the phenotypes.txt file of resfinder_db for gene OXA-244
            oxa_cmd="sed -i 's/\(blaOXA-244_1_KP659189\)\(\tBeta-lactam\)\(\tUnknown Beta-lactam\)/\\1\\2\tAmoxicillin, Amoxicillin+Clavulanic acid, Ampcillin, Ampicillin+Clavulanic acid, Imipenem, Meropenem, Piperacillin, Piperacillin+Tazobactam/' phenotypes.txt"
            os.system(oxa_cmd)
            os.chdir(current_dir)
        return version
    
    def download_db_pointfinder(self, version):
        """Function to download pointfinder database if it is not present"""
        pointfinder_db_dir = self.db_dir.joinpath("pointfinder_db")
        current_dir = os.getcwd()
        if not pointfinder_db_dir.joinpath("config").is_file():
            print("\x1b[0;33m Downloading pointfinder database...\n\033[0;0m")
            hf.download_git_repo(
                version,
                "https://bitbucket.org/genomicepidemiology/pointfinder_db.git",
                pointfinder_db_dir
            )
            os.chdir(pointfinder_db_dir)
            os.system(f"python3 INSTALL.py")
            os.chdir(current_dir)
        return version

    def get_downloads_juno_amr(
            self,
            software_virulence_finder_asked_version,
            software_resfinder_asked_version,
            db_resfinder_asked_version,
            db_virulencefinder_asked_version,
            db_pointfinder_asked_version,
            ):
                if self.update_dbs:
                    try:
                        rm_dir = subprocess.run(
                            ["rm", "-rf", str(self.db_dir)], check=True, timeout=60
                            )
                    except:
                        rm_dir.kill()
                        raise
                software_version = {
                    'resfinder': self.download_software_resfinder(version=software_resfinder_asked_version),
                    'virulencefinder': self.download_software_virulencefinder(version=software_virulence_finder_asked_version),
                    'resfinder_db': self.download_db_resfinder(version=db_resfinder_asked_version),
                    'pointfinder_db': self.download_db_pointfinder(version=db_pointfinder_asked_version),
                    'virulencefinder_db': self.download_db_virulencefinder(version=db_virulencefinder_asked_version)
                }
                return software_version

    if __name__ == '__main__':
        argument_parser = argparse.ArgumentParser(
             description="Dowload databases for Juno-amr"
        )
        argument_parser.add_argument(
        "-d",
        "--db-dir",
        type=pathlib.Path,
        default="db",
        help="Database directory where the databases will be stored.",
        )
        argument_parser.add_argument(
            "-sr",
            "--software-resfinder-version",
            type=str,
            default="4.6.0",
            help="Version to download for resfinder software.",
        )
        argument_parser.add_argument(
            "-sv",
            "--software-virulencefinder-version",
            type=str,
            default="2.0.4",
            help="Version to download for virulencefinder software.",
        )
        argument_parser.add_argument(
            "-dbv",
            "--database-virulencefinder-version",
            type=str,
            default="master",
            help="Version to download for virulencefinder database.",
        )
        argument_parser.add_argument(
            "-dbr",
            "--database-resfinder-version",
            type=str,
            default="master",
            help="Version to download for resfinder database.",
        )
        argument_parser.add_argument(
            "-dbp",
            "--database-pointfinder-version",
            type=str,
            default="master",
            help="Version to download for pointfinder database.",
        )
        argument_parser.add_argument("--update", dest="update_dbs", action="store_true")
        args = argument_parser.parse_args()
        downloads = DownloadsJunoAmr(
            db_dir=args.db_dir,
            update_dbs=args.update_dbs,
            software_resfinder_asked_version=args.software_resfinder_version,
            software_virulencefinder_asked_version=args.software_virulencefinder_asked_version,
            db_pointfinder_asked_version=args.database_pointfinder_version,
            db_resfinder_asked_version=args.database_resfinder_version,
            db_virulencefinder_asked_version=args.database_virulencefinder_version,)
