"""
Wrapper made in python for the juno-amr pipeline
"""

#imports
import sys
import argparse
import os

def get_user_arguments(givenargs):
 #   """Function to parse the command line arguments from the user"""

    # Create argparser
    parser = argparse.ArgumentParser(
        #place example of run here, how to make arguments positional/optional?
        usage= "amr_wrapper.py ....",
        description = "Juno-amr pipeline. Automated pipeline to use resfinder and pointfinder on given input data.",
        add_help = True
    )

    # Check if directory exists
    def isDirectory(input_dir):
        if os.path.isdir(input_dir):
            return input_dir
        else:
            print(f'\"{input_dir}\" is not a directory. Give an existing directory.')
            sys.exit(1)

    #Add input directory argument
    parser.add_argument(
        "-i",
        "--input",
        type=isDirectory,
        required=True,
        metavar="",
        dest="input_dir",
        #For now the only input accepted is a fasta file, need to decide on fasta or fastq
        help="Path to the directory of your input. Example: path/to/input/fasta or path/to/input/fastq"
    )

    # Add species argument
    parser.add_argument(
        "-s",
        "--species",
        type = str,
        required = True,
        metavar="",
        dest="species",
        # Later replace underscore with space for resfinder input[put in between quotes?]
        help = "Full scientific name of the species sample, use underscores not spaces. Example: Campylobacter_spp. Options to choose from: Campylobacter_spp, Campylobacter_jejuni, Campylobacter_coli, Escherichia_coli, Salmonella_spp, Plasmodium_falciparum, Neisseria_gonorrhoeae, Mycobacterium_tuberculosis, Enterococcus_faecalis, Enterococcus_faecium, Klebsiella, Helicobacter_pylori & Staphylococcus_aureus",
        #space does not work on commandline, reason why the names are with underscore
        #Currently with capital letter, remove or not?
        # use nargs?
        choices = ["Campylobacter_spp", "Campylobacter_jejuni", "Campylobacter_coli", "Escherichia_coli", "Salmonella_spp", "Plasmodium_falciparum", "Neisseria_gonorrhoeae", "Mycobacterium_tuberculosis", "Enterococcus_faecalis", "Enterococcus_faecium", "Klebsiella", "Helicobacter_pylori", "Staphylococcus_aureus"]
    )

    # Add coverage argument
    parser.add_argument(
        #Default value?
        "-l",
        "--min_cov",
        type=float,
        required=True,
        metavar="",
        dest="coverage",
        help="Minimum coverage of ResFinder"
    )

    # Add identity threshold argument
    parser.add_argument(
        #Default value?
        "-t",
        "--threshold",
        type=float,
        required=True,
        metavar="",
        dest="threshold",
        help="Threshold for identity of resfinder"
    )

    # parse and print args to the command line
    args = parser.parse_args()
    #print(args.input_dir)

        #Add .fna, .ffn, .frn as well?
    # allowed_file_extensions = [".faa", ".fasta"]
    # def isCorrectInputFormat(allowed_file_extensions, args):
    #     input_dir = args.input_dir
    #     for filename in os.listdir(input_dir):
    #         name, file_extension = os.path.splitext(filename)
    #         print(name, "testing", file_extension)
     
    #     # check if the files in the existing directory end with .fa .fasta
    #     # if true continue
    #     # if false
    #     # or fastq files?
    #     # print("This directory does not contain any fasta files")

    # isCorrectInputFormat(allowed_file_extensions, args)


    # Check if arguments were given, if no arguments were given give instructions.
    if len(givenargs)<1:
        print(f"{parser.prog} was called but no arguments were given, please try again. \n\tUse '{parser.prog} -h' to show all available options.")
        sys.exit(1)
    else:
        flags = parser.parse_args(givenargs)

    return flags

    #def validate_input_path(args):
     #   print(args.input_dir)
    

def main():
    flags = get_user_arguments(sys.argv[1:]),
    #validate_input_path()

if __name__ == '__main__':
    main()