import sys
import os
from pathlib import Path

def get_species_names_from_pointfinder_db(path_to_pointfinder_db):
    species_options = []
    if Path(path_to_pointfinder_db).is_dir():
        print("Database present, collect species from database")
        for entry in os.scandir(path_to_pointfinder_db):
            if not entry.name.startswith('.') and entry.is_dir():
                species_options.append(entry.name)    
    else:
        print("No database found, using local file to collect species")
        #TODO hardcoded path
        with open("files/pointfinder_species.txt") as f:
            species_options = f.readlines()
            species_options = [species.strip() for species in species_options]

    species_options.append("other")
    return species_options

# def check_species():
#     # check if species matches other
#     for key in dict_arguments:
#         if key == "species":
#             species = dict_arguments[key]
#             if species == "other":
#                 # if species is other turn off pointfinder
#                 for key in dict_arguments:
#                     if key == "run_pointfinder":
#                         dict_arguments[key] = dict_arguments[key] = "0"
#                         return dict_arguments

#             else:
#                 return dict_arguments

def change_species_name_format(argument_dict):
    # change _ to " " in species name & update species name in the arguments
    argument_dict.species = argument_dict.species.replace("_", " ")
    return argument_dict
