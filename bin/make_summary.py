"""
Juno-amr
Authors: Roxanne Wolthuis ....
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium Surveillance (IDS), Bacteriologie (BPD)
Date: 30 - 03 - 2021
Documentation: -
"""

from operator import index
from statistics import mode
import sys
import argparse
from pandas.core.arrays.sparse import dtype
import yaml
import csv
import os
import pandas as pd
from pathlib import Path
import shutil

class JunoSummary:
    def __init__(self, arguments=None):
        self.user_parameters_path = "config/user_parameters.yaml"
        self.summary_folder_path = "summary"
        self.results_folder = "results_per_sample"
        self.antibiotics_ecoli_salm = ["ampicillin", "cefotaxime", "ciprofloxacin", "gentamicin", "meropenem", "sulfamethoxazole", "trimethoprim", "cotrimoxazole", "azithromycin"]
        self.antibiotics_camp = ["ciprofloxacin", "gentamicin", "erythromycin", "tetracycline"]

    def get_user_arguments(self):
        """Function to parse the command line arguments from the user"""
        # Create argparser
        self.parser = argparse.ArgumentParser(
            usage= "python3 juno-amr.py -s [species]  -i [directory with fastq files]",
            description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
            add_help = True
        )

        self.parser.add_argument(
            "-sr",
            "--summary_resfinder",
            #TODO TYPE is een path of file
            type=str,
            metavar="file",
            dest="resfinder_summary_file_names",
            # 2 different filenames are requested. The first one is for the gene summary, second phenotype summary
            # TODO Do we want a default for this?
            nargs=2,
            help="The name for each of the resfinder summary files(max 2 files), in this order: gene_summary, phenotype_summary."
        )

        self.parser.add_argument(
            "-si",
            "--summary_iles",
            #TODO TYPE is een path of file
            type=str,
            metavar="file",
            dest="iles_summary_file_names",
            nargs=1,
            help="The name for the iles summary file"
        )

        self.parser.add_argument(
            "-sp",
            "--summary_pointfinder",
            type=str,
            metavar="file",
            dest="pointfinder_summary_file_names",
            #  2 different filenames are requested. The first one is for pointfinder result summary and second poinfinder prediction summary
            nargs=2,
            help="The name for each of the pointfinder summary files(max 2 files), in this order: Pointfinder_result_summary, pointfinder_prediction_summary."
        )

        self.parser.add_argument(
            "-sv",
            "--summary_virulencefinder",
            type=str,
            metavar="file",
            dest="virulencefinder_summary_file_names",
            nargs=1,
            help="The name for the virulencefinder summary file for example: virulencefinder_summary"
        )

        self.parser.add_argument(
            "-sa",
            "--summary_amrfinderplus",
            type=str,
            metavar="file",
            dest="amrfinderplus_summary_file_names",
            nargs=1,
            help="The name for the amrfinderplus summary file for example: amrfinderplus_summary"
        )
        self.parser.add_argument(
            "-i",
            "--input",
            type=str,
            required= True,
            metavar="dir",
            dest="input",
            # For the amount of samples there has to be at least one
            nargs='+',
            help="The input directory for each sample?"
            
        )
        
        self.parser.add_argument(
            "-st",
            "--summary_type",
            type=str,
            required = True,
            metavar="name",
            dest="summary_type",
            help="The type of summaries to create, choose from: resfinder, pointfinder, amrfinderplus or virulencefinder",
            choices= ["resfinder", "pointfinder", "amrfinderplus", "virulencefinder", "iles"]
        )

        # parse arguments
        self.dict_arguments = vars(self.parser.parse_args())
    
    def preproccesing_for_summary_files(self):
        #Get the output directory from the yaml file
        open_config_parameters = open(self.user_parameters_path)
        parsed_config = yaml.load(open_config_parameters, Loader=yaml.FullLoader)
        self.output_dir_name = parsed_config['out']
        self.species = parsed_config['species']
        
        # Make new summary directory
        dirpath = Path(f"{self.output_dir_name}/{self.summary_folder_path}")
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        #get samples from the sample directory
        self.input_paths = self.dict_arguments.get("input")
        self.samplenames = []
        for path in self.input_paths:
            path.strip("'")
            elements = path.split("/")
            samplename = elements[-1]
            self.samplenames.append(samplename)

        #Collect summary file names from the parser
        self.resfinder_summary_file_names = self.dict_arguments.get("resfinder_summary_file_names")
        self.pointfinder_summary_file_names = self.dict_arguments.get("pointfinder_summary_file_names")
        self.iles_summary_file_names = self.dict_arguments.get("iles_summary_file_names")
        self.virulencefinder_summary_file_names = self.dict_arguments.get("virulencefinder_summary_file_names")
        self.amrfinderplus_summary_file_names = self.dict_arguments.get("amrfinderplus_summary_file_names")
        return self.output_dir_name, self.samplenames, dirpath

    def create_amr_genes_summary(self):
        genes_summary_location = self.resfinder_summary_file_names[0]

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
        self.pheno_summary_location = self.resfinder_summary_file_names[1]
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
        pointfinder_results_output = self.pointfinder_summary_file_names[0]
        
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

            pathname = f"{path}/PointFinder_results.txt" 
            opened_file = open(pathname, "r")
            lines = opened_file.readlines()
            subselection = lines[1:]
            

            # If pointfinder has no results, write an empty list to the summary
            for line in subselection:
                sample = []

                if len(line) < 1:
                    # append hier lege values voor alle columns 
                    sample.extend((self.samplenames[sample_counter], None, None, None, None, None))
                # if there is result, place it in a list and convert this to a pd dataframe
                
                else:
                    sample.append(self.samplenames[sample_counter])
                    elements = line.split("\t")
                    for element in elements:
                        sample.append(element)
                
                data_per_sample.append(sample)    
            sample_counter = sample_counter + 1

        data_frame = pd.DataFrame(data_per_sample, columns = column_names)
        data_frame.to_csv(f'{pointfinder_results_output}', mode='a', index=False)
    
    def pointfinder_prediction_summary(self):
        #Get path & open 1 file for the colnames
        pointfinder_prediction_output = self.pointfinder_summary_file_names[1]
        
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
    
    def iles_summary(self):
        """Summary file specific for iles/lims"""

        self.species = self.species.replace(" ", "_")
        sample_counter_pheno_table = 0
        sample_counter_pointfinder = 0
        df_list = []
        df_list_point = []

        #loop over for pheno table
        for filename in self.input_paths:
            dirpath = f"{filename}/pheno_table.txt"
            opened_file = open(dirpath, "r")
            #select lines starting with 'antimicrobial'
            data_lines = opened_file.readlines()[17:]

            df = pd.DataFrame([x.split('\t') for x in data_lines], dtype='object')
            df.columns=['Antimicrobial', 'Class', 'WGS-predicted phenotype', 'Match', 'Genetic background']

            #select antimicrobial rows per species
            #TODO dit kan samen met wat helemaal onderaan staat
            if self.species == "escherichia_coli" or self.species == "salmonella":
                filtered_df = df.loc[df['Antimicrobial'].isin(self.antibiotics_ecoli_salm)]
            elif self.species == "campylobacter":
                filtered_df = df.loc[df['Antimicrobial'].isin(self.antibiotics_camp)]

            else:
                print("No iles summary for this species")
                return

            selected_rows  = filtered_df[["Antimicrobial", "WGS-predicted phenotype", "Genetic background"]].copy()
            selected_rows.loc[selected_rows['WGS-predicted phenotype'] == "Resistant", 'WGS-predicted phenotype'] = selected_rows['Genetic background']
            final = selected_rows[["Antimicrobial", "WGS-predicted phenotype"]].copy()

            #flip the df
            final.set_index('Antimicrobial',inplace=True)
            transposed = final.transpose()
            transposed.insert(0,"samplename", self.samplenames[sample_counter_pheno_table])
            sample_counter_pheno_table = sample_counter_pheno_table + 1
            df_list.append(transposed)
        
        #loop over for pointfinder file
        for filename in self.input_paths:
            dirpath = f"{filename}/PointFinder_results.txt"
            opened_file = open(dirpath, "r")
            pointfinder_data = opened_file.readlines()[1:]
            mut_res_combos = []
            # get the mutation and resistance
            for line in pointfinder_data:
                    line = line.split("\t")
                    mutation = line[0]
                    resistance = line[3].split(",")
                    unique_resistance = []
                    for x in resistance:
                        x = x.strip(" ")
                        if x not in unique_resistance:
                            unique_resistance.append(x)

                    #link the mutation to the resistance
                    for x in unique_resistance:
                        dictlist = [mutation, x]
                        mut_res_combos.append(dictlist)

            #create df
            df = pd.DataFrame(mut_res_combos, columns=["0","1"])
            print("df")
            print(df.to_string())
            df = df.set_index('1')
            transposed = df.transpose()
            transposed.columns= transposed.columns.str.lower()

            #TODO get nalicilix acid out of the cols

            #select only the used antimicrobials
            if self.species == "escherichia_coli" or self.species == "salmonella":   
                filtered_transposed = transposed.filter(regex='|'.join(self.antibiotics_ecoli_salm))
            elif self.species == "campylobacter":
                filtered_transposed = transposed.filter(regex='|'.join(self.antibiotics_camp))
            else:
                print("No iles summary for this species")
                return

            complete_df = filtered_transposed.astype(str).groupby(filtered_transposed.columns, axis=1).agg(lambda x: x.apply(','.join, 1))
            complete_df.insert(0,"samplename", self.samplenames[sample_counter_pointfinder])
            df_list_point.append(complete_df)
            sample_counter_pointfinder = sample_counter_pointfinder + 1

        final_df_point = pd.concat(df_list_point)    
        final_df = pd.concat(df_list, axis=0, ignore_index=True)
        final_df.columns= final_df.columns.str.lower()
        inner_merged_total = pd.merge(final_df_point, final_df, on=["samplename"], how="inner")
        inner_merged_total = inner_merged_total.replace(",", " ", regex=True)
        inner_merged_total = inner_merged_total.replace("\n", "", regex=True)

        #remove suffix to combine columns
        inner_merged_total.columns = inner_merged_total.columns.str.rstrip('_x')
        inner_merged_total.columns = inner_merged_total.columns.str.rstrip('_y')
        final_combined = inner_merged_total.groupby(level=0, axis=1).first()

        if self.species == "escherichia_coli" or self.species == "salmonella":    
            final_combined.filter(regex='|'.join(self.antibiotics_ecoli_salm))
        elif self.species == "campylobacter":
            final_combined.filter(regex='|'.join(self.antibiotics_camp))
        else:
            print("No iles summary for this species")
            return

        if self.species == "escherichia_coli" or self.species == "salmonella":
            #if trimepthoprim or sulfamethoxazole == no resistance then cotrimoxazole == no resistance, because there is no resistance against one of the two means that there is no resistance
            if "No resistance" in final_combined["trimethoprim"].values or "No resistance" in final_combined["sulfamethoxazole"].values:
                final_combined["cotrimoxazole"] = "No resistance"
            else:
                final_combined["cotrimoxazole"] = final_combined[["trimethoprim", "sulfamethoxazole"]].agg(" ".join, axis=1)

        col_name = "samplename"
        first_col = final_combined.pop(col_name)
        final_combined.insert(0, col_name, first_col)
        final_combined.to_csv(self.iles_summary_file_names[0], index=False)
    def virulencefinder_summary(self):
        virulence_summary_location = self.virulencefinder_summary_file_names[0]
        sample_counter = 0
        dflist = []
        for path in self.input_paths:
            pathname = f"{path}/results_tab.tsv"
            opened_file = pd.read_csv(pathname, sep="\t", dtype=object, keep_default_na=False)
            filtered_df = opened_file.filter(['Virulence factor', 'Identity', 'Query / Template length', 'Protein function'], axis=1)
            filtered_df.insert(0, "Samplename", self.samplenames[sample_counter])   
            sample_counter = sample_counter + 1  
            dflist.append(filtered_df)
        
        final_df = pd.concat(dflist, axis=0, ignore_index=True)
        final_df.to_csv(virulence_summary_location, mode='a', index=False)

    def amrfinderplus_summary(self):
        amrfinderplus_summary_location = self.amrfinderplus_summary_file_names[0]
        sample_counter = 0
        dflist = []
        for path in self.input_paths:
            pathname = f"{path}/amrfinder_result.txt"
            opened_file = pd.read_csv(pathname, sep="\t", dtype=object, keep_default_na=False)
            filtered_df = opened_file.filter(['Gene symbol', 'Sequence name', 'Element type', 'Element subtype', 'Class', 'Subclass', '% Coverage of reference sequence', '% Identity to reference sequence'], axis=1)
            filtered_df.insert(0, "Samplename", self.samplenames[sample_counter])   
            sample_counter = sample_counter + 1  
            dflist.append(filtered_df)
        
        final_df = pd.concat(dflist, axis=0, ignore_index=True)
        final_df.to_csv(amrfinderplus_summary_location, mode='a', index=False)

def main():
    m = JunoSummary()
    m.get_user_arguments()
    m.preproccesing_for_summary_files()
    summary_type = m.dict_arguments.get("summary_type")

    if summary_type == "resfinder":
        m.create_amr_genes_summary()
        m.add_header_to_phenotype_summary()
        m.create_amr_phenotype_summary()

    elif summary_type == "pointfinder":
        m.pointfinder_result_summary()
        m.pointfinder_prediction_summary()
    
    elif summary_type == "amrfinderplus":
        m.amrfinderplus_summary()
    
    elif summary_type == "virulencefinder":
        m.virulencefinder_summary()

    elif summary_type == "iles":
        m.iles_summary()

if __name__ == '__main__':
    main()