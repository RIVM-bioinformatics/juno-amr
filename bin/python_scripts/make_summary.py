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
import csv
import os
import pandas as pd
from pathlib import Path
import shutil

class JunoSummary:
    def __init__(self, arguments=None):
        """constructor"""

    def preproccesing_for_summary_files(self):
        #Get the output directory from the yaml file
        open_config_parameters = open("config/user_parameters.yml")
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        self.output_dir_name = parsed_config['Parameters']['output_dir']
        
        # if there is a summary directory, delete this
        dirpath = Path(f"{self.output_dir_name}/summary")
        if dirpath.exists() and dirpath.is_dir():
            print("found summary directory, removing it")
            shutil.rmtree(dirpath)
        
        # Make new summary directory
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        #get samples from the sample directory
        self.samplenames = os.listdir(f"{self.output_dir_name}/results_per_sample")
        return self.output_dir_name, self.samplenames, dirpath

    def create_amr_genes_summary(self):
        #receive input from snakemake
        #genes_output_file = snakemake.input[0]
        genes_output_file = f"{self.output_dir_name}/results_per_sample"
        #receive output from snakemake
        genes_summary_location = snakemake.output[0]
        
        #write genedata to outputfile
        with open(genes_summary_location, 'w', newline='') as csvfile:
            summary_file = csv.writer(csvfile)

            #Set the header for the file
            #Just taking the first sample to get the header for the csv file
            pathname = f"{genes_output_file}/{self.samplenames[0]}/ResFinder_results_tab.txt"
            opened_file = open(pathname, "r")

            #get the column names
            header = opened_file.readline().split("\t")
            del header[4:]
            header.insert(0, "Sample")
            summary_file.writerow(header)

            # for each sample get the data
            for samplename  in self.samplenames:
                # Open file and collect all data except the header
                pathname = f"{genes_output_file}/{samplename}/ResFinder_results_tab.txt"
                opened_file = open(pathname, "r")
                data_lines = opened_file.readlines()[1:]

                #Write elements of interest to the generated summary file
                for line in data_lines:
                    elements_in_line = line.split("\t")
                    del elements_in_line[4:]
                    elements_in_line.insert(0, samplename)
                    summary_file.writerow(elements_in_line)

    def add_header_to_phenotype_summary(self):
        #Create the summary file for the phenotype
        pheno_summary_location = snakemake.output[1]
        #TODO make this snakemake input(ook in andere functie) --> self.phenotype_output_file = snakemake.input[0]
        self.phenotype_output_file = f"{self.output_dir_name}/results_per_sample"
        
        with open(pheno_summary_location, 'w', newline='') as csvfile:
            summary_file = csv.writer(csvfile)

        #Set the informational header for the file
        #Just taking the first sample to get the header for the csv file
            pathname = f"{self.phenotype_output_file}/{self.samplenames[0]}/pheno_table.txt" 
            opened_file = open(pathname, "r")
            header = opened_file.readlines()
            header_selection = header[7:16]
            for string in header_selection:
                summary_file.writerow([string])
    
    def create_amr_phenotype_summary(self):           
        #set boolean for colnames true here
        add_colnames = True
        pheno_summary_location = snakemake.output[0]
        #Create empty list to store the dataframes for each sample
        self.df_list = []

        for samplename in self.samplenames:
            # empty list for antimicrobial classes
            antimicrobials = []
            # add sample name column
            antimicrobials.insert(0, "Samplename")
            #Make an empty list for the file content
            file_content = []
            #Make empty list for each sample and add the samplename to the sample column
            antimicrobial_match = []
            antimicrobial_match.insert(0, samplename)
            #Open the resfinder results
            pathname = f"{self.phenotype_output_file}/{samplename}/pheno_table.txt"
            opened_file = open(pathname, "r")
            #Make subselection of the file starting line 17 where the antimicrobial classes are listed
            #TODO make it based on the header
            sub_selection = opened_file.readlines()[17:]
            
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
        final_df.to_csv(f'{self.output_dir_name}/summary/summary_amr_phenotype.csv', mode='a', index=False)

def main():
    m = JunoSummary()
    m.preproccesing_for_summary_files()
    m.create_amr_genes_summary()
    m.add_header_to_phenotype_summary()
    m.create_amr_phenotype_summary()

if __name__ == '__main__':
    main()