import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import warnings
import json
import pathlib
import concurrent.futures
warnings.filterwarnings("ignore")
import time

root_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(root_dir)
write_dir = os.path.join(root_dir, "Data_HEP")

from derived_quantities import  DER_data
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import argparse


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

    
def generate_weight_table(keys, file_read_loc, crosssection_dict,luminocity):
    number_of_events_dict = {}
    weights_dict = {}    
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
                
    for key in number_of_events_dict.keys():
        try:
            weights_dict[key] = (crosssection_dict[key]["crosssection"] * luminocity / number_of_events_dict[key] )
        
        except KeyError:
            print(f"[*] --- {key} not found in crosssection_dict")
            weights_dict[key] = -1
                       
    return weights_dict

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

    train_settings = {
        "tes": 1.0,
        "jes": 1.0,
        "soft_met": 0.0,
        "ttbar_scale": 1.0,
        "diboson_scale": 1.0,
        "bkg_scale": 1.0,
        "ground_truth_mu": 1.0,
    }    
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


def train_test_data_generator(full_data, test_factor=2, train_factor = 8):


    # Remove the "label" and "weights" columns from the data    
    test_set = {}
    train_set = {}
    sample_set = {}
    print("\n[*] -- full_data")
    for key in full_data.keys():
        lhc_numbers = int(np.sum(full_data[key]["Weight"]))
        print("lhc_numbers", lhc_numbers)
        print("test_factor", test_factor)
        print("train_factor", train_factor)
        
      
        if key == "htautau":
            print(f"[*] --- {key} : {full_data[key].shape}")
            test_number  = (lhc_numbers * test_factor)
            train_set[key], test_set[key] = train_test_split(
                full_data[key], test_size=int(test_number), random_state=42
            )            
        
        else :
            
            print(f"[*] --- {key} : {full_data[key].shape}")

            try:
                test_number  = (lhc_numbers * test_factor) - 1
                train_number = (lhc_numbers * train_factor) - 1
                sample_set[key] , test_set[key] = train_test_split(
                    full_data[key], test_size=int(test_number), random_state=42
                )
                
                _ , train_set[key] = train_test_split(sample_set[key], test_size=int(train_number), random_state=42)
                
                
            except ValueError as e:
                print(f"ValueError at {key}, full shape={full_data[key].shape[0]}")
                print(f"ValueError at {key}, sample shape={sample_set[key].shape[0]}")
                print(f"ValueError at {key}, test shape={test_number}")
                print(f"ValueError at {key}, train shape={train_number}")
                
                raise e
           
    return train_set, test_set

def sample_data_generator(full_data, Full_size=0.3, Test_size=0.3):

    # Remove the "label" and "weights" columns from the data    
    test_set = {}
    train_set = {}
    sample_set = {}
    print("\n[*] -- full_data")
    for key in full_data.keys():
        print(f"[*] --- {key} : {full_data[key].shape}")
        lhc_numbers = int(np.sum(full_data[key]["Weight"]))
        full_number  = (lhc_numbers) * Full_size
        _ , sample_set[key] = train_test_split(
            full_data[key], test_size=int(full_number), random_state=42
        )

        test_number  = (full_number * Test_size)
        train_set[key], test_set[key] = train_test_split(
            sample_set[key], test_size=int(test_number), random_state=42
        )
                              
    return train_set, test_set 

def weighting(process_flag,weight_table):
    process_flag = np.array(process_flag)
    weights = np.zeros(len(process_flag))
    print(f"[*] --- process_flag shape : {process_flag.shape}")
    process_flag = process_flag.astype(int)
    for key in weight_table.keys():
        weights[process_flag == int(key)] = weight_table[key]
    return weights

def reweight(weights, sum_weights_full):
    weights = np.array(weights)
    sum_weights = np.sum(weights) 
    weights = weights * sum_weights_full / sum_weights 
    
    return weights

def dataGenerator(input_file_loc=os.path.join(root_dir, "input_data"),
                  output_file_loc=write_dir,
                  input_format = "csv",
                  output_format = "Parquet",
                  derived_quantities = True,
                  verbose=0,
                  concurrent_processing = False,
                  test_factor = 2,
                  public_train_factor = 8,
                  public_test_factor = 2,
                  luminosity = 36):

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
    
    crossection_file = os.path.join(root_dir, "crosssection.json")

    with open(crossection_file) as f:
        crosssection_dict = json.load(f)

    weight_table = generate_weight_table(full_data.keys(), input_file_loc, crosssection_dict, luminosity)

    for key in full_data.keys():
        print(f"[*] Weighting {key}")
        print(f"[*] --- {key} : {full_data[key].shape}")
        full_set_weights = weighting(full_data[key]["Process_flag"], weight_table)
        full_data[key]["Weight"] = full_set_weights
        print(f"[*] --- {key} : {full_data[key]['Weight'].sum()}")

    public_factor = public_train_factor + public_test_factor
    train_set, test_set = train_test_data_generator(full_data,  test_factor = test_factor, train_factor = public_factor)
    
    print("\n[*] -- test_set")
    def process_test_set(key):
        print(f"[*] --- {key} : {test_set[key].shape}")
        test_weights = reweight(test_set[key]["Weight"], full_data[key]["Weight"].sum())
        test_set[key].pop("Label")
        test_set[key].pop("Process_flag")
        test_set[key].pop("Weight")
        test_set[key].round(3)
        test_set[key]["weights"] = test_weights
        test_set[key].drop( test_set[key][ test_weights < 0 ].index , inplace=True)
        test_set[key].reset_index(drop=True, inplace=True)
        print(f"[*] --- {key} : {test_set[key].shape}")
        print(f"[*] --- {key} : {test_weights.sum()}")


    if concurrent_processing:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(process_test_set, test_set.keys()))
    else:
        for key in test_set.keys():
            process_test_set(key)


    print("\n[*] -- train_set")
    def process_train_set(key):
        train_set[key]["detailed_label"] = key
        if key == "htautau":
            train_set[key]["Label"] = 1
        train_set[key]["Weight"] = reweight(train_set[key]["Weight"], full_data[key]["Weight"].sum())
        print(f"[*] --- {key} : {train_set[key].shape}")
        print(f"[*] --- {key} : {train_set[key]['Weight'].sum()}")
    
    if concurrent_processing:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(process_train_set, train_set.keys()))
    else:
        for key in train_set.keys():
            process_train_set(key)
        
    print("\n[*] Saving test data")
    save_test_data(test_set, os.path.join(output_file_loc, "challenge_data"), output_format)
    
    del test_set, full_data
    
    public_train_set , public_test_set  = train_test_data_generator(train_set, test_factor = public_test_factor, train_factor = public_train_factor)

    
    public_train_list = []
    print("\n[*] -- public_train_set")
    def process_public_train_set(key):
        print(f"[*] --- {key} : {public_train_set[key].shape}")
        public_train_set[key]["Weight"] = reweight(public_train_set[key]["Weight"], train_set[key]["Weight"].sum())
        public_train_list.append(public_train_set[key])
        print(f"[*] --- {key} : {public_train_set[key]['Weight'].sum()}")

    if concurrent_processing:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(process_public_train_set, public_train_set.keys()))
    else:
        for key in public_train_set.keys():
            process_public_train_set(key)

    public_train_df = pd.concat(public_train_list)
    public_train_df = public_train_df.sample(frac=1).reset_index(drop=True)
    public_train_label = public_train_df.pop("Label")
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
    
    print("\n[*] Saving public train data")
    save_train_data(public_train_data_set, os.path.join(output_file_loc,"public_data"), output_format)


    print("\n[*] Saving Train data")
    save_train_data(public_train_data_set, os.path.join(output_file_loc,"challenge_data"), output_format)

    print("\n[*] Saving public test data")
    def process_public_test_set(key):
        print(f"[*] --- {key} : {public_test_set[key].shape}")
        public_test_weights = reweight(public_test_set[key]["Weight"], train_set[key]["Weight"].sum())    
        public_test_set[key].pop("Label")
        public_test_set[key].pop("Process_flag")
        public_test_set[key].pop("detailed_label")
        public_test_set[key].pop("Weight")
        public_test_set[key].round(3)
        public_test_set[key]["weights"] = public_test_weights
        print(f"[*] --- {key} : {public_test_set[key]['weights'].sum()}")
        
    if concurrent_processing:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(process_public_test_set, public_test_set.keys()))
    else:   
        for key in public_test_set.keys():
            process_public_test_set(key)

    save_test_data(public_test_set, os.path.join(output_file_loc, "public_data"), output_format)

    sample_train_set, sample_test_set = sample_data_generator(train_set, Full_size=0.3, Test_size=0.3)

    sample_train_list = []
    print("\n[*] -- sample_train_set")
    for key in sample_train_set.keys():
        print(f"[*] --- {key} : {sample_train_set[key].shape}")
        sample_train_set[key]["Weight"] = reweight(sample_train_set[key]["Weight"], train_set[key]["Weight"].sum())
        sample_train_list.append(sample_train_set[key])
        print(f"[*] --- {key} : {sample_train_set[key]['Weight'].sum()}")

    sample_train_df = pd.concat(sample_train_list)
    sample_train_df = sample_train_df.sample(frac=1).reset_index(drop=True)
    sample_train_label = sample_train_df.pop("Label")
    sample_train_df.pop("Process_flag")
    sample_train_detailed_labels = sample_train_df.pop("detailed_label")
    sample_train_weights = sample_train_df.pop("Weight")
    sample_train_df = sample_train_df.round(3)

    sample_train_data_set = {"data": sample_train_df, "labels": sample_train_label, "weights": sample_train_weights, "detailed_labels": sample_train_detailed_labels}

    if verbose > 0:
        print("Sample_set")
        print(sample_train_df.columns)
        print(f"[*] --- sum of weights : {np.sum(sample_train_weights)}")
        print(f"[*] --- sum of signal : {np.sum(sample_train_weights[sample_train_label==1])}")
        print(f"[*] --- sum of background : {np.sum(sample_train_weights[sample_train_label==0])}")
        
    print("\n[*] Saving sample train data")

    save_train_data(sample_train_data_set, os.path.join(output_file_loc,"sample_data"), output_format)
    
    print("\n[*] Saving sample test data")
    for key in sample_test_set.keys():
        print(f"[*] --- {key} : {sample_test_set[key].shape}")
        sample_test_weights = reweight(sample_test_set[key]["Weight"], train_set[key]["Weight"].sum())
        sample_test_set[key].pop("Label")
        sample_test_set[key].pop("Process_flag")
        sample_test_set[key].pop("detailed_label")
        sample_test_set[key].pop("Weight")
        sample_test_set[key].round(3)
        sample_test_set[key]["weights"] = sample_test_weights
        print(f"[*] --- {key} : {sample_test_set[key]['weights'].sum()}")
        
        if verbose > 0 :
            print(sample_test_set[key].columns)
            print(sample_test_set[key].shape)

    save_test_data(sample_test_set, os.path.join(output_file_loc, "sample_data"), output_format)

    date = time.strftime("%d_%m_%Y")
                
    zipdir(f"input_data_{date}.zip",os.path.join(output_file_loc, "challenge_data", "input_data"))
    zipdir(f"reference_data_{date}.zip",os.path.join(output_file_loc, "challenge_data","reference_data"))
    zipdir(f"public_data_{date}.zip",os.path.join(output_file_loc, "public_data"))
    zipdir(f"sample_input_data_{date}.zip",os.path.join(output_file_loc, "sample_data", "input_data"))
    zipdir(f"sample_reference_data_{date}.zip",os.path.join(output_file_loc, "sample_data", "reference_data"))


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
                        "-I",
                        type=str,
                        help="format of the input file",
                        choices ={"csv","parquet"} ,
                        default="csv")
    parser.add_argument("--output-format",
                        "-O",
                        type=str,
                        help="format of the output file", 
                        choices ={"csv","parquet"} ,
                        default="csv")
    parser.add_argument("--derived-quantities", 
                        "-d", 
                        help="Add derived quantities to the data",
                        action="store_true",
                        default=False)
    parser.add_argument("--parallel", 
                        "-p",
                        help="Use parallel processing",
                        action="store_true",
                        default=False)
    parser.add_argument("--test-factor", 
                        "-t", 
                        help="Factor to multiply the test data",
                        type=int,
                        default=2)
    parser.add_argument("--public-train-factor",
                        "-P", 
                        help="Factor to multiply the public train data",
                        type=int,
                        default=5)
    parser.add_argument("--public-test-factor",
                        "-T",
                        help="Factor to multiply the public test data",
                        type=int,
                        default=5)
    parser.add_argument("--luminocity",
                        "-L",
                        help="Luminocity of the data",
                        type=int,
                        default=36)  
     
    args = vars(parser.parse_args())
    
    print("root - dir", root_dir)
    print("parent - dir", parent_dir)
    
    start_time = time.time()

    dataGenerator(input_file_loc = args["input"],
                    output_file_loc = args["output"],
                    input_format = args["input_format"],
                    output_format = args["output_format"],
                    derived_quantities = args["derived_quantities"],
                    concurrent_processing=args["parallel"],
                    verbose=1,
                    test_factor = args["test_factor"],
                    public_train_factor = args["public_train_factor"],
                    public_test_factor = args["public_test_factor"],
                    luminosity = args["luminocity"]
                    )
    
    end_time = time.time()
    
    print(f"[*] --- Time taken : {end_time - start_time} seconds")
    
    