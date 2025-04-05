import sys
import os
import argparse
import pandas as pd
from pathlib import Path
import uproot
import numpy as np
import json


def process_counter(output_file_name):
    
    # Open the ROOT file using uproot
    with uproot.open(output_file_name + ".root") as file:
        # Access the histogram
        process_hist = file["process_ID"]
        
        # Convert histogram to numpy arrays
        bin_edges = process_hist.axis().edges()
        bin_contents = process_hist.values()
        
        process_dict = {}
        for i, content in enumerate(bin_contents):
            if content > 0:
                print("Process ID: ", i)
                print(content)
                process_dict[i] = content
        
        # Save the dictionary as a JSON file
        with open(output_file_name + ".json", "w") as f:
            json.dump(process_dict, f)
    
    return process_dict


def root_to_pandas(root_file_path, tree_name):
    """
    Convert a ROOT NTuple to a Pandas DataFrame.
    
    Parameters:
    - root_file_path: Path to the ROOT file
    - tree_name: Name of the TTree in the ROOT file
    
    Returns:
    - Pandas DataFrame containing the TTree data
    """
    # Open the ROOT file
    file = uproot.open(root_file_path)
    
    # Access the TTree
    tree = file[tree_name]
    
    # Convert to Pandas DataFrame
    df = tree.arrays(library="pd")
    
    return df

def generate_weight_table(key,number_of_events, crosssection_dict,luminocity):
    number_of_events_dict = {}
    weights_dict = {}    
                
    for key in number_of_events_dict.keys():
        try:
            weights_dict[key] = (crosssection_dict[key]["crosssection"] * luminocity / number_of_events_dict[key] )
        
        except KeyError:
            print(f"[*] --- {key} not found in crosssection_dict")
            weights_dict[key] = -1
                       
    return weights_dict

def clean_data(data_set):
    for key in data_set.keys():
        df = data_set[key]
        df = df.drop_duplicates()
        print(f"[*] -#- {key} : {df.shape}")
        df.pop("PRI_lep_charge")
        df.pop("PRI_had_charge")
        df.pop("PRI_jet_leading_charge")
        df.pop("PRI_jet_subleading_charge")
        df.pop("PRI_muon_flag")
        df.pop("PRI_electron_flag")

        df.reset_index(drop=True, inplace=True)

        print(f"[*] -#- {key} : {df.shape}")

        try:
            df.pop('Unnamed: 0')
        except KeyError:
            print("No Unnamed: 0 column")

        try:
            df.pop('entry')
        except KeyError:
            print("No entry column")


        df = df.astype(np.float32)

        data_set[key] = df
        
        del df
        
    return data_set


def to_parquet(data, output_file_name):
    parquet_file_name = output_file_name.with_suffix(".parquet")
    data.to_parquet(parquet_file_name)
    print("Data saved as parquet file")

def to_csv(data, output_file_name):
    csv_file_name = output_file_name.with_suffix(".csv")
    data.to_csv(csv_file_name)
    print("Data saved as csv file")
    
if __name__ == "__main__":

    
    merged_file_name = "Merged_output.csv"

    parser = argparse.ArgumentParser(
        description="This is script to merge csv files together into one."
    )
    parser.add_argument("--input", "-i", help="Input file location")
    parser.add_argument("--output", "-o", help="Output file location")
    parser.add_argument(
        "--remove", "-r", action="store_true", help="Remove redundant files"
    )
    parser.add_argument(
        "--parquet", "-p", action="store_true", help="Convert merged data to parquet"
    )

    args = parser.parse_args()

    if args.output:
        merged_file_path = Path(args.output)
    else:
        merged_file_path = Path.cwd() / merged_file_name

    if args.input:
        file_read_loc = Path(args.input)
    else:
        print("Please provide input file location")
        raise ValueError("Input file location is required.")
    
    process_dict = process_counter(file_read_loc.stem)
