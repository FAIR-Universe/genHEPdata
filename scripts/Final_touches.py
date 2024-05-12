import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import warnings
import json
import pathlib

warnings.filterwarnings("ignore")
import sys

root_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(root_dir)
write_dir = os.path.join(root_dir, "Data_HEP")

systematics_path = os.path.join(parent_dir, "HEP-Challenge", "ingestion_program")

sys.path.append(systematics_path)
from derived_quantities import  DER_data
from config import LHC_NUMBERS, DICT_CROSSSECTION, LUMINOCITY
from data_io import zipdir

import argparse


# Load the csv file
def clean_data(data_set):
    for key in data_set.keys():
        df = data_set[key]
        df = df.drop_duplicates()
        df.pop("entry")
        df.pop("PRI_lep_charge")
        df.pop("PRI_had_charge")
        df.pop("PRI_jet_leading_charge")
        df.pop("PRI_jet_subleading_charge")
        df.pop("PRI_muon_flag")
        df.pop("PRI_electron_flag")
        df.pop('Unnamed: 0')

        df.sample(frac=1).reset_index(drop=True)
        df = DER_data(df)
        data_set[key] = df
        
    return data_set


def from_csv(data, file_read_loc):
    for file in os.listdir(file_read_loc):
        if file.endswith(".csv"):
            file_path = os.path.join(file_read_loc, file)
            key = file.split(".")[0]
            if key in data:
                data[key] = pd.read_csv(file_path)
            else:
                print(f"Invalid key: {key}")
        else:
            print("No csv file found")

def save_train_data(data_set, file_write_loc, output_format="csv"):
        # Create directories to store the label and weight files
    train_label_path = os.path.join(file_write_loc,"input_data", "train", "labels")
    if not os.path.exists(train_label_path):
        os.makedirs(train_label_path)

    train_weights_path = os.path.join(file_write_loc,"input_data", "train", "weights")
    if not os.path.exists(train_weights_path):
        os.makedirs(train_weights_path)

    train_data_path = os.path.join(file_write_loc,"input_data", "train", "data")
    if not os.path.exists(train_data_path):
        os.makedirs(train_data_path)

    train_detailed_labels_path = os.path.join(file_write_loc,"input_data", "train", "detailed_labels")
    if not os.path.exists(train_detailed_labels_path):
        os.makedirs(train_detailed_labels_path)


    train_settings_path = os.path.join(file_write_loc,"input_data", "train", "settings")
    if not os.path.exists(train_settings_path):
        os.makedirs(train_settings_path)

    train_settings = {"tes": 1.0, "jes" : 1.0,"soft_met" :1.0, "w_scale": 1.0,"bkg_scale" : 1.0 ,"ground_truth_mu": 1.0}
    # Specify the file path
    Settings_file_path = os.path.join(train_settings_path, "data.json")

    # Save the settings to a JSON file
    with open(Settings_file_path, "w") as json_file:
        json.dump(train_settings, json_file, indent=4)


    if output_format == "csv" :
        train_data_path = os.path.join(train_data_path, "data.csv")
        data_set["data"].to_csv(train_data_path, index=False)
        
    elif output_format == "parquet" :
        train_data_path = os.path.join(train_data_path, "data.parquet")
        data_set["data"].to_parquet(train_data_path, index=False)

    # Save the label, detailed_labels and weight files for the training set
    train_labels_file = os.path.join(train_label_path,"data.labels")
    data_set["labels"].to_csv(train_labels_file, index=False, header=False)
        
    train_weights_file = os.path.join(train_weights_path,"data.weights")
    data_set["weights"].to_csv(train_weights_file, index=False, header=False)
    
    train_detailed_labels_file = os.path.join(train_detailed_labels_path,"data.detailed_labels")
    data_set["detailed_labels"].to_csv(train_detailed_labels_file, index=False, header=False)
    
def save_test_data(data_set, file_write_loc, output_format="csv"):
    # Create directories to store the label and weight files
    reference_settings_path = os.path.join(file_write_loc, "reference_data", "settings")
    if not os.path.exists(reference_settings_path):
        os.makedirs(reference_settings_path)

    test_data_loc = os.path.join(file_write_loc,"input_data", "test", "data")
    if not os.path.exists(test_data_loc):
        os.makedirs(test_data_loc)

    test_settings_path = os.path.join(file_write_loc,"input_data", "test", "settings")
    if not os.path.exists(test_settings_path):
        os.makedirs(test_settings_path)

    for key in data_set.keys():
        
        if output_format == "csv" :
            if not os.path.exists(test_data_loc):
                os.makedirs(test_data_loc)
            test_data_path = os.path.join(test_data_loc, f"{key}_data.csv")

            data_set[key].to_csv(test_data_path, index=False)

        if output_format == "parquet" :
            if not os.path.exists(test_data_loc):
                os.makedirs(test_data_loc)             
            test_data_path = os.path.join(test_data_loc, f"{key}_data.parquet")
           
            data_set[key].to_parquet(test_data_path, index=False)

    mu = np.random.uniform(0, 3, 10)
    mu = np.round(mu, 3)
    mu_list = mu.tolist()
    print(f"[*] --- mu in test set : ", mu_list)

    test_settings = {"ground_truth_mus": mu_list}
    Settings_file_path = os.path.join(reference_settings_path, "data.json")
    with open(Settings_file_path, "w") as json_file:
        json.dump(test_settings, json_file, indent=4)

    Settings_file_path = os.path.join(test_settings_path, "data.json")
    with open(Settings_file_path, "w") as json_file:
        json.dump(test_settings, json_file, indent=4)

def from_parquet(data, file_read_loc):
    for file in os.listdir(file_read_loc):
        if file.endswith(".parquet"):
            file_path = os.path.join(file_read_loc, file)
            key = file.split(".")[0]
            if key in data:
                data[key] = pd.read_parquet(file_path)
            else:
                print(f"Invalid key: {key}")
        else:
            print("No parquet file found")


def train_test_data_generator(full_data, verbose=0):


    # Remove the "label" and "weights" columns from the data    
    test_set = {}
    train_set = {}

    print("\n[*] -- full_data")
    for key in full_data.keys():
        print(f"[*] --- {key} : {full_data[key].shape}")
        try:
            train_set[key], test_set[key] = train_test_split(
                full_data[key], test_size=int(LHC_NUMBERS[key] * 0.01), random_state=42
            )
        except ValueError:
            print(f"ValueError at {key}, test_size={int(LHC_NUMBERS[key] * 0.01)} and shape={full_data[key].shape}")
            

    return train_set, test_set


def reweight(process_flag, crosssection_dict=DICT_CROSSSECTION):
    # Temporary fix for the reweighting issue

    crossection_list = crosssection_dict["crosssection"]
    process_list = crosssection_dict["process_flags"]
    number_of_events = crosssection_dict["number"]

    weights = np.zeros(len(process_flag))
    for i in range(len(process_flag)):
        index = process_list.index(process_flag[i])
        weights[i] = crossection_list[index] * LUMINOCITY / number_of_events[index]        

    return weights

def dataGenerator(input_file_loc=os.path.join(root_dir, "input_data"),
                  output_file_loc=write_dir,
                  input_format = "csv",
                  output_format = "Parquet",
                  verbose=0):

    full_data = {
        "Z": pd.DataFrame(),
        "W": pd.DataFrame(),
        "Diboson": pd.DataFrame(),
        "TT": pd.DataFrame(),
        "H": pd.DataFrame(),
    }

    if input_format == "csv" :
        # Load the data from the csv files
        from_csv(full_data,input_file_loc)

    elif input_format == "parquet":
        # Load the data from the parquet files
        from_parquet(full_data,input_file_loc)
    else :
        print("Unknown Format")

    full_data = clean_data(full_data)

    train_set, test_set = train_test_data_generator(full_data, verbose=verbose)

    train_list = []
    print("\n[*] -- train_set")
    for key in train_set.keys():
        train_set[key]["detailed_label"] = key
        if key == "H":
            train_set[key]["Label"] = 1
        train_list.append(train_set[key])
        print(f"[*] --- {key} : {train_set[key].shape}")


    train_df = pd.concat(train_list)
    train_df = train_df.sample(frac=1).reset_index(drop=True)

    train_label = train_df.pop("Label")
    train_df["Weight"] = reweight(train_df["Process_flag"])
    train_df.pop("Process_flag")
    train_detailed_labels = train_df.pop("detailed_label")
    train_weights = train_df.pop("Weight")
    train_df = train_df.round(3)
    
    train_data_set = {"data": train_df, "labels": train_label, "weights": train_weights, "detailed_labels": train_detailed_labels}

    if verbose > 0:
        print(train_df.columns)

    if verbose > 0:
        print(f"[*] --- sum of weights : {np.sum(train_weights)}")
        print(f"[*] --- sum of signal : {np.sum(train_weights[train_label==1])}")
        print(f"[*] --- sum of background : {np.sum(train_weights[train_label==0])}")

    save_train_data(train_data_set, os.path.join(output_file_loc,"challenge_data"), output_format)

    for key in test_set.keys():
        print(f"[*] --- {key} : {test_set[key].shape}")
        test_set[key].pop("Label")
        test_set[key].pop("Process_flag")
        test_set[key].pop("Weight")
        test_set[key].round(3)
        
        
        if verbose > 0 :
            print(test_set[key].columns)

    save_test_data(test_set, os.path.join(output_file_loc, "challenge_data"), output_format)
    
    public_train_set , public_test_set = train_test_data_generator(train_set, verbose=verbose)
    
    public_train_list = []
    print("\n[*] -- public_train_set")
    for key in public_train_set.keys():
        print(f"[*] --- {key} : {public_train_set[key].shape}")
        public_train_list.append(public_train_set[key])

    public_train_df = pd.concat(public_train_list)
    public_train_df = public_train_df.sample(frac=1).reset_index(drop=True)

    public_train_label = public_train_df.pop("Label")
    public_train_df["Weight"] = reweight(public_train_df["Process_flag"])
    public_train_df.pop("Process_flag")
    public_train_detailed_labels = public_train_df.pop("detailed_label")
    public_train_weights = public_train_df.pop("Weight")
    public_train_df = public_train_df.round(3)
    
    public_train_data_set = {"data": public_train_df, "labels": public_train_label, "weights": public_train_weights, "detailed_labels": public_train_detailed_labels}
    
    if verbose > 0:
        print(public_train_df.columns)

    if verbose > 0:
        print(f"[*] --- sum of weights : {np.sum(public_train_weights)}")
        print(f"[*] --- sum of signal : {np.sum(public_train_weights[public_train_label==1])}")
        print(f"[*] --- sum of background : {np.sum(public_train_weights[public_train_label==0])}")
    
    save_train_data(public_train_data_set, os.path.join(output_file_loc,"public_data"), output_format)
    
    for key in public_test_set.keys():
        print(f"[*] --- {key} : {public_test_set[key].shape}")
        public_test_set[key].pop("Label")
        public_test_set[key].pop("Process_flag")
        public_test_set[key].pop("Weight")
        public_test_set[key].round(3)
        
        
        if verbose > 0 :
            print(public_test_set[key].columns)

    save_test_data(public_test_set, os.path.join(output_file_loc, "public_data"), output_format)
            
    zipdir("input_data.zip",os.path.join(output_file_loc,"challenge_data","input_data"))
    zipdir("reference_data.zip",os.path.join(output_file_loc, "challenge_data","reference_data"))
    zipdir("public_data.zip",os.path.join(output_file_loc, "public_data"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This is script to generate data for the HEP competition."
    )
    parser.add_argument("--input", 
                        "-i", 
                        type=pathlib.Path,
                        help="Input file location",
                        )
    parser.add_argument("--output", 
                        "-o", 
                        type=pathlib.Path,
                        help="Output file location",
                        )
    parser.add_argument("--input-format", 
                        type=str,
                        help="format of the input file",
                        choices ={"csv","parquet"} ,
                        default="csv")
    parser.add_argument("--output-format",
                        type=str,
                        help="format of the output file", 
                        choices ={"csv","parquet"} ,
                        default="csv")
    
    args = vars(parser.parse_args())
    
    print("root - dir", root_dir)
    print("parent - dir", parent_dir)

    dataGenerator(args["input"],args["output"],args["input_format"],args["output_format"],verbose=1)
