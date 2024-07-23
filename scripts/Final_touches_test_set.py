import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import warnings
import json
import pathlib
import concurrent.futures
warnings.filterwarnings("ignore")

root_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(root_dir)
write_dir = os.path.join(root_dir, "Data_HEP")

from derived_quantities import  DER_data
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
from multiprocessing import Pool

LUMINOCITY = 36  # 1/fb

LHC_NUMBERS = {
    "ztautau": 3574068,
    "diboson": 13602,
    "ttbar": 159079,
    "htautau": 3653,
}

# -------------------------------------
# Zip files
# -------------------------------------
def zipdir(archivename, basedir):
    '''Zip directory, from J.F. Sebastian http://stackoverflow.com/'''
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(basedir):
            # NOTE: ignore empty directories
            for fn in files:
                if fn[-4:] != '.zip' and fn != '.DS_Store':
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(basedir):]  # XXX: relative path
                    z.write(absfn, zfn)



def from_parquet(data, file_read_loc):
    for file in os.listdir(file_read_loc):
        if file.endswith(".parquet"):
            file_path = os.path.join(file_read_loc, file)
            key = file.split(".")[0]
            if key in data:
                data[key] = pd.read_parquet(file_path, engine="pyarrow")
            else:
                print(f"Invalid key: {key}")

            

def from_csv(data, file_read_loc):
    for file in os.listdir(file_read_loc):
        if file.endswith(".csv"):
            file_path = os.path.join(file_read_loc, file)
            key = file.split(".")[0]
            if key in data:
                data[key] = pd.read_csv(file_path,dtype=np.float32,index_col= False)
            else:
                print(f"Invalid key: {key}")

    
def combine_number_of_events(keys, file_read_loc):
    number_of_events_dict = {}    
    for file in os.listdir(file_read_loc):
        if file.endswith(".json"):
            file_path = os.path.join(file_read_loc, file)
            
            print(f"[*] --- file_path : {file_path}")
            
            key = file.split(".")[0]
            if key in keys:
                with open(file_path) as f:
                    number_of_events = json.load(f)
                    for key in number_of_events.keys():
                        number_of_events_dict[key] = number_of_events[key]        
            else:
                print(f"Invalid key: {key}")
                    
    return number_of_events_dict

# Load the csv file
def clean_data(data_set, derived_quantities=True):
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

        # change - 7 to -25
        leading_cols = ["PRI_jet_leading_eta", "PRI_jet_leading_phi", "PRI_jet_leading_pt"]
        for col in leading_cols:
            index = df[df[col] == -7].index
            df.loc[index, col] = -25

        subleading_cols = ["PRI_jet_subleading_eta", "PRI_jet_subleading_phi", "PRI_jet_subleading_pt"]
        for col in subleading_cols:
            index = df[df[col] == -7].index
            df.loc[index, col] = -25

        if derived_quantities:
            df = DER_data(df)
            
        df = df.astype(np.float32)

        data_set[key] = df
        
        del df
        
    return data_set
    
def save_test_data(data_set, file_write_loc, output_format="csv"):

    test_data_loc = os.path.join(file_write_loc,"test", "data")
    if not os.path.exists(test_data_loc):
        os.makedirs(test_data_loc)

    test_settings_path = os.path.join(file_write_loc,"test", "settings")
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

    Settings_file_path = os.path.join(test_settings_path, "data.json")
    with open(Settings_file_path, "w") as json_file:
        json.dump(test_settings, json_file, indent=4)


def test_data_generator(full_data, test_factor = 2):


    # Remove the "label" and "weights" columns from the data    
    test_set = {}
    factor_table = {}
    print("\n[*] -- full_data")
    for key in full_data.keys():
        print(f"[*] --- {key} : {full_data[key].shape}")
        try:
            test_number  = (LHC_NUMBERS[key]*test_factor)
            _, test_set[key] = train_test_split(
                full_data[key], test_size=int(test_number), random_state=42
            )
        except ValueError:
            print(f"ValueError at {key}, test_size={int(LHC_NUMBERS[key]*2)} and shape={full_data[key].shape[0]*0.3}")

            
        factor_table[key] = test_set[key].shape[0] / full_data[key].shape[0]

    return test_set , factor_table

def reweight(process_flag, detailed_label, crosssection_dict,number_of_events,factor_table):
    process_flag = np.array(process_flag)
    detailed_label = np.array(detailed_label)
    weights = np.zeros(len(process_flag))
    print(f"[*] --- detailed_label shape : {detailed_label.shape}")
    print(f"[*] --- process_flag shape : {process_flag.shape}")
    print(f"[*] --- weights shape : {weights.shape}")
    process_flag = process_flag.astype(int)
    for key in number_of_events.keys():
        try:
            weight = (crosssection_dict[key]["crosssection"] * LUMINOCITY / number_of_events[key] ) 
        except KeyError:
            print(f"[*] --- {key} not found in crosssection_dict")
            weight = -1

        for i in range(len(process_flag)):
            if process_flag[i] == int(key):
                weights[i] = weight / factor_table[detailed_label[i]]
    return weights

def dataGenerator(input_file_loc=os.path.join(root_dir, "input_data"),
                  output_file_loc=write_dir,
                  input_format = "Parquet",
                  output_format = "Parquet",
                  derived_quantities = True,
                  test_factor = 2):

    full_data = {
        "diboson": pd.DataFrame(),
        "ttbar": pd.DataFrame(),
        "htautau": pd.DataFrame(),
        "ztautau": pd.DataFrame(),

    }

    if input_format == "csv" :
        # Load the data from the csv files
        from_csv(full_data,input_file_loc)

    elif input_format == "parquet":
        # Load the data from the parquet files
        from_parquet(full_data,input_file_loc)
    else :
        print("Unknown Format")

    print("full_data :")    
    for key in full_data.keys():
        print(f"[*] --- {key} : {full_data[key].shape}")
      
    

    full_data = clean_data(full_data, derived_quantities=derived_quantities)
        

    test_set, factor_table_test = test_data_generator(full_data, test_factor=test_factor)

    number_of_events = combine_number_of_events(full_data.keys(), input_file_loc)
    
    with open("new_crosssection.json") as f:
        crosssection_dict = json.load(f)

    print("\n[*] -- test_set")
    def process_test_set(key):
        print(f"[*] --- {key} : {test_set[key].shape}")
        test_set[key]["detailed_label"] = key
        test_weights = reweight(test_set[key]["Process_flag"], test_set[key]["detailed_label"] ,crosssection_dict,number_of_events, factor_table_test)    
        test_set[key].pop("Label")
        test_set[key].pop("Process_flag")
        test_set[key].pop("detailed_label")
        test_set[key].pop("Weight")
        test_set[key].round(3)
        test_set[key]["weights"] = test_weights
        test_set[key].drop( test_set[key][ test_weights < 0 ].index , inplace=True)
        test_set[key].reset_index(drop=True, inplace=True)
        print(f"[*] --- {key} : {test_set[key].shape}")
        print(f"[*] --- {key} : {test_weights.sum()}")


    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(executor.map(process_test_set, test_set.keys()))

        
    print("\n[*] Saving test data")
    save_test_data(test_set, output_file_loc, output_format)
    
    del test_set, full_data
            
    zipdir("test_data.zip",os.path.join(output_file_loc,""))
    print("\n[*] --- Done")


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
    parser.add_argument("--derived-quantities", 
                        "-d", 
                        help="Add derived quantities to the data",
                        action="store_true",
                        default=False)
    parser.add_argument("--test-factor", 
                        "-t", 
                        help="Factor to multiply the test data",
                        type=int,
                        default=2)
    
    args = vars(parser.parse_args())
    
    print("[*] Input file location  :", args["input"])
    print("[*] Output file location :", args["output"])

    dataGenerator(input_file_loc = args["input"],
                    output_file_loc = args["output"],
                    input_format = args["input_format"],
                    output_format = args["output_format"],
                    derived_quantities = args["derived_quantities"],
                    test_factor = args["test_factor"])