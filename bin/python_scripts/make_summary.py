"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

import sys
import yaml

class JunoSummary:
    def __init__(self, arguments=None):
        """constructor"""

    def test(self):
        print("Hello world")

    def preproccesing_for_summary_files(self):
        #Get the output directory from the yaml file
        open_config_parameters = open("config/user_parameters.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        output_dir_name = parsed_config['Parameters']['output_dir']

        print(output_dir_name)
        # #current_path = os.path.abspath(os.getcwd())
        # #create the file path variab;e
        # self.output_file_path = f"{output_dir_name}"
        
        # # if there is a summary directory, delete this
        # dirpath = Path(f"{self.output_file_path}/summary")
        # if dirpath.exists() and dirpath.is_dir():
        #     print("found summary directory, removing it")
        #     shutil.rmtree(dirpath)
        
        # # Make new summary directory
        # if not os.path.exists(dirpath):
        #     os.makedirs(dirpath)
    
        # #get samples from the sample directory
        # self.samplenames = os.listdir(f"{self.output_file_path}/results_per_sample")
        # print("output file path:", self.output_file_path)
        # print("samplenames: ", self.samplenames)

        # return self.output_file_path, self.samplenames, dirpath


def main():
    m = JunoSummary()
    m.test()
    m.preproccesing_for_summary_files()
    
if __name__ == '__main__':
    main()