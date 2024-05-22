import sys
import os
import argparse
import pandas as pd
from pathlib import Path
import shutil

#!/usr/bin/env python3


def remove_redundant_files(file_read_loc):
    for file in os.listdir(file_read_loc):
        if file.endswith(".csv"):
            file_path = os.path.join(file_read_loc, file)
            os.remove(file_path)


class DataPreprocessing:

    def __init__(self, file_read_loc, data=None):
        columns = [
            "entry",
            "PRI_lep_pt",
            "PRI_lep_eta",
            "PRI_lep_phi",
            "PRI_lep_charge",
            "PRI_electron_flag",
            "PRI_muon_flag",
            "PRI_had_pt",
            "PRI_had_eta",
            "PRI_had_phi",
            "PRI_had_charge",
            "PRI_jet_leading_pt",
            "PRI_jet_leading_eta",
            "PRI_jet_leading_phi",
            "PRI_jet_leading_charge",
            "PRI_n_jets",
            "PRI_jet_subleading_pt",
            "PRI_jet_subleading_eta",
            "PRI_jet_subleading_phi",
            "PRI_jet_subleading_charge",
            "PRI_jet_all_pt",
            "PRI_met",
            "PRI_met_phi",
            "Weight",
            "Label",
            "Process_flag",
        ]
        data_frames = []
        if data is not None:
            data_frames.append(data)
        for file in os.listdir(file_read_loc):
            if file.endswith(".csv"):
                file_path = os.path.join(file_read_loc, file)
                try :
                    data = pd.read_csv(file_path)
                except:
                    print(f"Error reading file: {file_path}")
                    os.remove(file_path)
                    root_hist_file = file_path.replace(".csv", "_cuthist.root")
                    os.remove(root_hist_file)
                    continue
                data.columns = columns
                data_frames.append(data)
                

        self.data = pd.concat(data_frames)
        print(self.data.describe())

    def to_parquet(self, output_file_name):
        parquet_file_name = output_file_name.with_suffix(".parquet")
        self.data.to_parquet(parquet_file_name)
        print("Data saved as parquet file")

    def to_csv(self, output_file_name):
        csv_file_name = output_file_name.with_suffix(".csv")
        self.data.to_csv(csv_file_name)
        print("Data saved as csv file")


if __name__ == "__main__":
    merged_file_name = "Merged_output.csv"

    parser = argparse.ArgumentParser(
        description="This is script to merge csv files together into one."
    )
    parser.add_argument("--input", "-i", help="Input file location")
    parser.add_argument("--output", "-o", help="Output file location")
    parser.add_argument("--append", "-a", help="Create new file")
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
        sys.exit()

    if args.append:
        file_name = merged_file_path
        if file_name.suffix == ".csv":
            data = pd.read_csv(file_read_loc)
        elif file_name.suffix == ".parquet":
            data = pd.read_parquet(file_read_loc)
        else:
            print("Invalid file format")
            sys.exit()
        data_preprocessing = DataPreprocessing(file_read_loc, data)
    else:
        data_preprocessing = DataPreprocessing(file_read_loc)

    if args.remove:
        remove_redundant_files(file_read_loc)

    if args.parquet:
        data_preprocessing.to_parquet(merged_file_path)
    else:
        data_preprocessing.to_csv(merged_file_path)
        
    for file in os.listdir(file_read_loc):
        if file.endswith(".json"):
            file_path = os.path.join(file_read_loc, file)
            output_file_path = os.path.join(merged_file_path, file)
            shutil.copy2(file_path, merged_file_path.with_suffix(".json"))
