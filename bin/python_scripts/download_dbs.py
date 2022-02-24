"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""
import pathlib
import subprocess
import os

def download_git_repo(version, url, dest_dir):
    """Function to download a git repo"""
    # Delete old output dir if existing and create parent dirs if not existing
    try:
        rm_dir = subprocess.run(['rm','-rf', str(dest_dir)], check = True, timeout = 60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
        rm_dir.kill()
        raise

    if not isinstance(dest_dir, pathlib.PosixPath):
        dest_dir = pathlib.Path(dest_dir)

    dest_dir.parent.mkdir(exist_ok = True)
    try:
        downloading = subprocess.run(['git', 'clone', 
                                        '-b', version, 
                                        '--single-branch', '--depth=1', 
                                        url, str(dest_dir)],
                                        check = True,
                                        timeout = 500)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
        downloading.kill()
        raise
    
def get_commit_git(gitrepo_dir):
    """Function to get the commit number from a folder (must be a git repo)"""
    try:
        commit = subprocess.check_output(['git', 
                                        '--git-dir', 
                                        '{}/.git'.format(str(gitrepo_dir)), 
                                        'log', '-n', '1', '--pretty=format:"%H"'],
                                        timeout = 30)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as err:
        commit.kill()
        raise                    
    return commit

def download_software_resfinder(resfinder_software_dir, version = '4.1.3'):
    """Function to download kmerfinder if it is not present"""
    if not isinstance(resfinder_software_dir, pathlib.PosixPath):
        resfinder_software_dir = pathlib.Path(resfinder_software_dir)
    if not resfinder_software_dir.joinpath('run_resfinder.py').is_file():
        print("\x1b[0;33m Downloading resfinder software...\n\033[0;0m")
        download_git_repo(version, 
                        'https://bitbucket.org/genomicepidemiology/resfinder.git',
                        resfinder_software_dir)
        
    return version

def download_software_virulencefinder(virulencefinder_software_dir, version = '2.0.4'):
    """Function to download kmerfinder if it is not present"""
    if not isinstance(virulencefinder_software_dir, pathlib.PosixPath):
        virulencefinder_software_dir = pathlib.Path(virulencefindersoftware_dir)
    if not virulencefinder_software_dir.joinpath('virulencefinder.py').is_file():
        print("\x1b[0;33m Downloading virulencefinder software...\n\033[0;0m")
        download_git_repo(version, 
                        'https://bitbucket.org/genomicepidemiology/virulencefinder.git',
                        virulencefinder_software_dir)
        
    return version

def download_db_resfinder(resfinder_db_dir):
    """Function to download resfinder database if it is not present"""
    if not isinstance(resfinder_db_dir, pathlib.PosixPath):
        resfinder_db_dir = pathlib.Path(resfinder_db_dir)
    if not resfinder_db_dir.joinpath('config').exists():
        print("\x1b[0;33m Downloading resfinder database...\n\033[0;0m")
        print(resfinder_db_dir)
        download_git_repo('master', 
                        'https://git@bitbucket.org/genomicepidemiology/resfinder_db.git',
                        resfinder_db_dir)
        try:
            current_dir = os.getcwd()
            os.chdir(resfinder_db_dir)
            os.system(f"python3 INSTALL.py")
            #Applying a change in the phenotypes.txt file of resfinder_db for gene OXA-244
            oxa_cmd="sed -i 's/\(blaOXA-244_1_KP659189\)\(\tBeta-lactam\)\(\tUnknown Beta-lactam\)/\\1\\2\tAmoxicillin, Amoxicillin+Clavulanic acid, Ampcillin, Ampicillin+Clavulanic acid, Imipenem, Meropenem, Piperacillin, Piperacillin+Tazobactam/' phenotypes.txt"
            os.system(oxa_cmd)
            os.chdir(current_dir)
        except (OSError, IOError) as err:
            print("OS error: ", err)
            raise

    version = get_commit_git(resfinder_db_dir)
    return version

def download_db_pointfinder(pointfinder_db_dir):
    """Function to download pointfinder database if it is not present"""
    if not isinstance(pointfinder_db_dir, pathlib.PosixPath):
        pointfinder_db_dir = pathlib.Path(pointfinder_db_dir)
    if not pointfinder_db_dir.joinpath('config').exists():
        print("\x1b[0;33m Downloading pointfinder database...\n\033[0;0m")
        download_git_repo('master', 
                        'https://bitbucket.org/genomicepidemiology/pointfinder_db.git',
                        pointfinder_db_dir)
        try:
            current_dir = os.getcwd()
            os.chdir(pointfinder_db_dir)
            os.system(f"python3 INSTALL.py")
            os.chdir(current_dir)
        except (OSError, IOError) as err:
            print("OS error: ", err)
            raise
    version = get_commit_git(pointfinder_db_dir)
    return version

def download_db_virulencefinder(virulencefinder_db_dir):
    """Function to download virulencefinder database if it is not present"""
    if not isinstance(virulencefinder_db_dir, pathlib.PosixPath):
        virulencefinder_db_dir = pathlib.Path(virulencefinder_db_dir)
    if not virulencefinder_db_dir.joinpath('config').exists():
        print("\x1b[0;33m Downloading virulencefinder database...\n\033[0;0m")
        print(virulencefinder_db_dir)
        download_git_repo('master', 
                        'https://bitbucket.org/genomicepidemiology/virulencefinder_db.git',
                        virulencefinder_db_dir)
        try:
            current_dir = os.getcwd()
            os.chdir(virulencefinder_db_dir)
            os.system(f"python3 INSTALL.py")
            os.chdir(current_dir)
        except (OSError, IOError) as err:
            print("OS error: ", err)
            raise

    version = get_commit_git(virulencefinder_db_dir)
    return version   

def get_downloads_juno_amr(db_dir, current_dir, update_dbs):
    if not isinstance(db_dir, pathlib.PosixPath):
        db_dir = pathlib.Path(db_dir)
    if not isinstance(current_dir, pathlib.PosixPath):
        current_dir = pathlib.Path(current_dir)
    if update_dbs:
        try:
            rm_dir = subprocess.run(['rm', '-rf', str(db_dir)], check = True, timeout = 60)
        except:
            rm_dir.kill()
            raise
    software_version = {'resfinder': download_software_resfinder(current_dir.joinpath('resfinder')),
                    'virulencefinder': download_software_virulencefinder(current_dir.joinpath('virulencefinder')),
                    'resfinder_db': download_db_resfinder(db_dir.joinpath('resfinderdb')),
                    'pointfinder_db': download_db_pointfinder(db_dir.joinpath('pointfinderdb')),
                    'virulencefinder_db': download_db_virulencefinder(db_dir.joinpath('virulencefinderdb'))}
    return software_version

if __name__ == '__main__':
    main()
