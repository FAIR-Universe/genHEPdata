import sys
import os
import argparse
import pandas as pd
from pathlib import Path
import uproot
import numpy as np
import json


def process_counter(root_file_path):
    

    with uproot.open(root_file_path) as file:
        # Check if the histogram exists
        if "process_ID;1" not in file:
            print("KEYS: ", file.keys())

            raise KeyError(f"Histogram 'process_ID;1' not found in the file: {root_file_path}")
        # Print the keys in the file
        
        # Access the histogram
        process_hist = file["process_ID;1"]
        
        # Convert histogram to numpy arrays
        bin_contents = process_hist.values()
        
        process_dict = {}
        for i, content in enumerate(bin_contents):
            if content > 0:
                print("Process ID: ", i)
                print(content)
                process_dict[i] = content
        
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

    # Convert the TTree to a Pandas DataFrame
    df = tree.arrays(library="pd")
    
    return df

def generate_weight_table(number_of_events, crosssection_dict, luminocity):
    
    # Convert the keys of crosssection_dict to integers
    crosssection_dict = {int(k): v for k, v in crosssection_dict.items()}
                
    for key in number_of_events.keys():
        weights_dict = {}
        
        if key in crosssection_dict.keys():
            print(f"[*] --- {key} found in crosssection_dict")

            weights_dict[key] = (crosssection_dict[key]["crosssection"] * luminocity / number_of_events[key] )
        
        else:
            print(f"[*] --- {key} not found in crosssection_dict")
            print(f"[*] --- keys in crosssection_dict: {crosssection_dict.keys()}")

            weights_dict[key] = -1
                       
    return weights_dict

def clean_data(df):

    df = df.drop_duplicates()
    df.pop("PRI_lep_charge")
    df.pop("PRI_had_charge")
    df.pop("PRI_jet_leading_charge")
    df.pop("PRI_jet_subleading_charge")
    df.pop("PRI_muon_flag")
    df.pop("PRI_electron_flag")

    df.reset_index(drop=True, inplace=True)


    try:
        df.pop('Unnamed: 0')
    except KeyError:
        print("No Unnamed: 0 column")

    try:
        df.pop('entry')
    except KeyError:
        print("No entry column")


    return df

def weighting(process_flag,weight_table):
    process_flag = np.array(process_flag)
    weights = np.zeros(len(process_flag))
    print(f"[*] --- process_flag shape : {process_flag.shape}")
    process_flag = process_flag.astype(int)
    for key in weight_table.keys():
        weights[process_flag == int(key)] = weight_table[key]
    return weights 
def to_parquet(data, output_file_name,metadata=None):
    parquet_file_name = output_file_name.with_suffix(".parquet")
    if metadata is not None:
        data.to_parquet(parquet_file_name, metadata=metadata)
    else:
        data.to_parquet(parquet_file_name)
    print("Data saved as parquet file")

def to_csv(data, output_file_name):
    csv_file_name = output_file_name.with_suffix(".csv")
    data.to_csv(csv_file_name)
    print("Data saved as csv file")
    
if __name__ == "__main__":

    root_dir = os.path.dirname(os.path.abspath(__file__))
    merged_file_name = "Merged_output.csv"

    parser = argparse.ArgumentParser(
        description="This is script to merge csv files together into one."
    )
    parser.add_argument("--input", "-i", help="Input file location")
    parser.add_argument("--output", "-o", help="Output file location")
    parser.add_argument(
        "--parquet", "-p", action="store_true", help="Convert merged data to parquet"
    )
    parser.add_argument("--luminocity", "-l", type=float, default=1.0, help="Luminocity value")

    args = parser.parse_args()

    if args.output:
        merged_file_path = Path(args.output)
    else:
        if args.parquet:
            merged_file_path = Path.cwd() / "Merged_output.parquet"
        else:
            merged_file_path = Path.cwd() / "Merged_output.csv"

    if args.input:
        file_read_loc = Path(args.input)
    else:
        print("Please provide input file location")
        raise ValueError("Input file location is required.")
    
    process_dict = process_counter(file_read_loc)

    crossection_file = os.path.join(root_dir, "crosssection.json")

    with open(crossection_file) as f:
        crosssection_dict = json.load(f)

    weight_table = generate_weight_table(process_dict, crosssection_dict, args.luminocity)

    df = root_to_pandas(file_read_loc, "physics;1")
    df = clean_data(df)

    df["weights"] = weighting(df["Process_flag"], weight_table)
    
    df.pop("Process_flag")
    
    df.rename(columns={"process_name": "detailed_labels"}, inplace=True)
    df.rename(columns={"Label": "labels"}, inplace=True)
    
    from derived_quantities import DER_data
    
    df = DER_data(df)
    
    sum_weights = df["Weight"].sum()
    meta_data = {
        "author": "FAIR Universe",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "detailed_labels": df["detailed_labels"].unique().tolist(),
        "sum_weights": float(df["weights"].sum()),  # Convert to native float
        "luminosity": 10,
    }
    
    meta_data_file = merged_file_path.with_name(merged_file_path.stem + "_metadata.json")
    with open(meta_data_file, "w") as f:
        json.dump(meta_data, f, indent=4)
    print(f"[*] --- Metadata saved to {meta_data_file}")    
        
    if args.parquet:
        to_parquet(df, merged_file_path)
    else:
        to_csv(df, merged_file_path)

