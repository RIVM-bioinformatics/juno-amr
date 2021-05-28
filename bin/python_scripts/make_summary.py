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
import yaml
import csv
import os
import pandas as pd
from pathlib import Path
import shutil

class JunoSummary:
    def __init__(self, arguments=None):
        self.user_parameters_path = "config/user_parameters.yml"
        self.summary_folder_path = "summary"
        self.results_folder = "results_per_sample"

    def get_user_arguments(self):
        """Function to parse the command line arguments from the user"""
        # Create argparser
        self.parser = argparse.ArgumentParser(
            usage= "python3 juno-amr.py -s [species]  -i [directory with fastq files]",
            description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
            add_help = True
        )

        self.parser.add_argument(
            "-s",
            "--summary",
            #TODO TYPE is een path of file
            type=str,
            required=True,
            metavar="file",
            dest="summary_file_names",
            # 4 different filenames are requested. The first one is for the gene summary, second phenotype summary, thirth pointfinder result summary and last poinfinder prediction summary
            # TODO Do we want a default for this?
            nargs = 4,
            help="The name for each of the summary files, in this order: gene_summary, phenotype_summary, Pointfinder_result_summary, pointfinder_prediction_summary"
        )

        self.parser.add_argument(
            "-i",
            "--input",
            type=str,
            required = True,
            metavar = "dir",
            dest = "input",
            # For the amount of samples there has to be at least one
            nargs = '+',
            help = "The input directory for each sample?"
            
        )
        
        # parse arguments
        self.dict_arguments = vars(self.parser.parse_args())
    
    def preproccesing_for_summary_files(self):
        #Get the output directory from the yaml file
        open_config_parameters = open(self.user_parameters_path)
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        self.output_dir_name = parsed_config['Parameters']['output_dir']
        
        # if there is a summary directory, delete this
        dirpath = Path(f"{self.output_dir_name}/{self.summary_folder_path}")
        if dirpath.exists() and dirpath.is_dir():
            print("found summary directory, removing it")
            shutil.rmtree(dirpath)
        
        # Make new summary directory
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        #get samples from the sample directory
        self.input_paths = self.dict_arguments.get("input")
        self.samplenames = []
        for path in self.input_paths:
            path.strip("'")
            elements = path.split("/")
            samplename = elements[2]
            self.samplenames.append(samplename)

        #Collect summary file names from the parser
        self.summary_file_names = self.dict_arguments.get("summary_file_names")

        return self.output_dir_name, self.samplenames, dirpath

    def create_amr_genes_summary(self):
        genes_summary_location = self.summary_file_names[0]

        #write genedata to outputfile
        with open(genes_summary_location, 'w', newline='') as csvfile:
            summary_file = csv.writer(csvfile)

            #Set the header for the file
            #Just taking the first sample to get the header for the csv file
            pathname = f"{self.input_paths[0]}/ResFinder_results_tab.txt"
            opened_file = open(pathname, "r")

            #get the column names
            header = opened_file.readline().split("\t")
            del header[4:]
            header.insert(0, "Sample")
            summary_file.writerow(header)

            # for each sample get the data
            # Set a counter to add the correct sample name for each sample
            sample_counter = 0
            for path in self.input_paths:
                pathname = f"{path}/ResFinder_results_tab.txt"
                opened_file = open(pathname, "r")
                data_lines = opened_file.readlines()[1:]

                #Write elements of interest to the generated summary file
                for line in data_lines:
                    elements_in_line = line.split("\t")
                    del elements_in_line[4:]
                    elements_in_line.insert(0, self.samplenames[sample_counter])
                    summary_file.writerow(elements_in_line)
                sample_counter = sample_counter + 1

    def add_header_to_phenotype_summary(self):
        self.pheno_summary_location = self.summary_file_names[1]
        with open(f"{self.pheno_summary_location}", 'w', newline='') as csvfile:
            summary_file = csv.writer(csvfile)

        #Set the informational header for the file
        #Just taking the first sample to get the header for the csv file
            pathname = f"{self.input_paths[0]}/pheno_table.txt" 
            opened_file = open(pathname, "r")
            header = opened_file.readlines()
            header_selection = header[7:16]
            for string in header_selection:
                summary_file.writerow([string])
    
    def create_amr_phenotype_summary(self):           
        #set boolean for colnames true here
        add_colnames = True
        #Create empty list to store the dataframes for each sample
        self.df_list = []

        sample_counter = 0
        for path in self.input_paths:
            # empty list for antimicrobial classes
            antimicrobials = []
            # add sample name column
            antimicrobials.insert(0, "Samplename")
            
            #Make an empty list for the file content
            file_content = []
            #Make empty list for each sample and add the samplename to the sample column
            antimicrobial_match = []

            antimicrobial_match.insert(0, self.samplenames[sample_counter])
            #Open the resfinder results
            pathname = f"{path}/pheno_table.txt"
            opened_file = open(pathname, "r")
            #Make subselection of the file starting line 17 where the antimicrobial classes are listed
            #TODO make it based on the header
            sub_selection = opened_file.readlines()[17:]
            sample_counter = sample_counter + 1

            for line in sub_selection:
                #Search for the end of the antimicrobial classes that are listed in the file
                if line.startswith("\n"):
                    break
                #Append all lines containing information to the file content list
                file_content.append(line)
            
            # Collect the antimicrobial names and their matches
            for line in file_content:
                elements = line.split("\t")
                antimicrobial_match.append(elements[3])
                antimicrobials.append(elements[0])
            
            # Create temp dataframe and store data
            temp_df = pd.DataFrame([antimicrobial_match], columns=antimicrobials)
            #Append df to a list with all the dfs 
            self.df_list.append(temp_df)

        # Merge all dataframes in one
        final_df = pd.concat(self.df_list, axis=0, ignore_index=True)
        #Write the dataframe to existing file with header
        final_df.to_csv(f'{self.pheno_summary_location}', mode='a', index=False)

    def pointfinder_result_summary(self):
        pointfinder_results_output = self.summary_file_names[2]
        
        #Get path & open 1 file for the colnames
        pathname = f"{self.input_paths[0]}/PointFinder_results.txt" 
        opened_file = open(pathname, "r")
        #Get columns from one of the files
        lines = opened_file.readlines()
        column_names = lines[0].split("\t")
        column_names.insert(0, "Samplename")

        # Make an empty list to add list with data for each sample
        data_per_sample = []

        #Collect data for each sample and add this to a list with the samplename
        sample_counter = 0
        for path in self.input_paths:
            sample = []
            pathname = f"{path}/PointFinder_results.txt" 
            opened_file = open(pathname, "r")
            lines = opened_file.readlines()
            subselection = lines[1:]

            sample.append(self.samplenames[sample_counter])
            for line in subselection:
                elements = line.split("\t")
                for element in elements:
                    sample.append(element)
            sample_counter = sample_counter + 1
            #Add samples to the list
            data_per_sample.append(sample)    

        #Create DF with pandas and write to csv file
        data_frame = pd.DataFrame(data_per_sample, columns = column_names)
        data_frame.to_csv(f'{pointfinder_results_output}', mode='a', index=False)
    
    def pointfinder_prediction_summary(self):
        #Get path & open 1 file for the colnames
        pointfinder_prediction_output = self.summary_file_names[3]
        
        dataframe_per_sample = []
        sample_counter = 0
        for path in self.input_paths: 
            pathname = f"{path}/PointFinder_prediction.txt" 
            opened_file = open(pathname, "r")
            lines = opened_file.readlines()

            #get the colnames
            column_names = lines[0].strip("\n").split("\t")
            # get the values
            elements = lines[1].strip("\n").split("\t")
            #add the samplename
            elements.insert(0, self.samplenames[sample_counter])
            #create df for each sample
            temp_df = pd.DataFrame([elements], columns=column_names)
            dataframe_per_sample.append(temp_df)
            sample_counter = sample_counter + 1
           
        #concat all dfs and write to file
        final_df = pd.concat(dataframe_per_sample, axis=0, ignore_index=True)
        final_df.to_csv(f'{pointfinder_prediction_output}', mode='a', index=False)
    
def main():
    m = JunoSummary()
    #m.get_species_names_from_pointfinder_db()
    m.get_user_arguments()
    m.preproccesing_for_summary_files()
    m.create_amr_genes_summary()
    m.add_header_to_phenotype_summary()
    m.create_amr_phenotype_summary()
    m.pointfinder_result_summary()
    m.pointfinder_prediction_summary()

if __name__ == '__main__':
    main()