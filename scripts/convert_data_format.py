import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import json
import os
import requests
from zipfile import ZipFile
import logging
import io
import argparse
from pathlib import Path
import sys



from  derived_quantities import DER_data


# Get the logging level from an environment variable, default to INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()


logging.basicConfig(
    level=getattr(
        logging, log_level, logging.INFO
    ),  # Fallback to INFO if the level is invalid
    format="%(asctime)s - %(name)-20s - %(levelname) -8s - %(message)s",
)

logger = logging.getLogger(__name__)


class Data:
    """
    A class to represent a dataset.

    Parameters:
        * input_dir (str): The directory path of the input data.

    Attributes:
        * __train_set (dict): A dictionary containing the train dataset.
        * __test_set (dict): A dictionary containing the test dataset.
        * input_dir (str): The directory path of the input data.

    Methods:
        * load_train_set(): Loads the train dataset.
        * load_test_set(): Loads the test dataset.
        * get_train_set(): Returns the train dataset.
        * get_test_set(): Returns the test dataset.
        * delete_train_set(): Deletes the train dataset.
        * get_syst_train_set(): Returns the train dataset with systematic variations.
    """

    def __init__(self, input_dir):
        """
        Constructs a Data object.

        Parameters:
            input_dir (str): The directory path of the input data.
        """

        self.__train_set = None
        self.__test_set = None
        self.input_dir = input_dir

    def load_train_set(self, sample_size=None, selected_indices=None):

        train_data_file = os.path.join(self.input_dir, "train", "data", "data.parquet")
        train_labels_file = os.path.join(
            self.input_dir, "train", "labels", "data.labels"
        )

        train_weights_file = os.path.join(
            self.input_dir, "train", "weights", "data.weights"
        )
        train_detailed_labels_file = os.path.join(
            self.input_dir, "train", "detailed_labels", "data.detailed_labels"
        )

        parquet_file = pq.ParquetFile(train_data_file)
        

        # Step 1: Determine the total number of rows
        total_rows = sum(parquet_file.metadata.row_group(i).num_rows for i in range(parquet_file.num_row_groups))

        if sample_size is not None:
            if isinstance(sample_size, int):
                sample_size = min(sample_size, total_rows)
            elif isinstance(sample_size, float):
                if 0.0 <= sample_size <= 1.0:
                    sample_size = int(sample_size * total_rows)
                else:
                    raise ValueError("Sample size must be between 0.0 and 1.0")
            else:
                raise ValueError("Sample size must be an integer or a float")
        elif selected_indices is not None:
            if isinstance(selected_indices, list):
                selected_indices = np.array(selected_indices)
            elif isinstance(selected_indices, np.ndarray):
                pass
            else:
                raise ValueError("Selected indices must be a list or a numpy array")
            sample_size = len(selected_indices)
        else:
            sample_size = total_rows

        if selected_indices is None:
            selected_indices = np.random.choice(total_rows, size=sample_size, replace=False)
        
        selected_indices = np.sort(selected_indices)

        selected_indices_set = set(selected_indices)

        def get_sampled_data(data_file):
            selected_list = []
            with open(data_file, "r") as f:
                for i, line in enumerate(f):
                    # Check if the current line index is in the selected indices
                    if i not in selected_indices_set:
                        continue
                    if data_file.endswith(".detailed_labels"):
                        selected_list.append(line.strip())
                    else:
                        selected_list.append(float(line.strip()))
                    # Optional: stop early if all indices are found
                    if len(selected_list) == len(selected_indices):
                        break
            return np.array(selected_list)

        current_row = 0
        sampled_df = pd.DataFrame()
        for row_group_index in range(parquet_file.num_row_groups):
            row_group = parquet_file.read_row_group(row_group_index).to_pandas()
            row_group_size = len(row_group)

            # Determine indices within the current row group that fall in the selected range
            within_group_indices = selected_indices[(selected_indices >= current_row) & (selected_indices < current_row + row_group_size)] - current_row
            sampled_df = pd.concat([sampled_df, row_group.iloc[within_group_indices]], ignore_index=True)

            # Update the current row count
            current_row += row_group_size

        selected_train_labels = get_sampled_data(train_labels_file)
        selected_train_weights = get_sampled_data(train_weights_file)
        selected_train_detailed_labels = get_sampled_data(train_detailed_labels_file)

        logger.info(f"Sampled train data shape: {sampled_df.shape}")
        logger.info(f"Sampled train labels shape: {selected_train_labels.shape}")
        logger.info(f"Sampled train weights shape: {selected_train_weights.shape}")
        logger.info(f"Sampled train detailed labels shape: {selected_train_detailed_labels.shape}")

        self.__train_set = {
            "data": sampled_df,
            "labels": selected_train_labels,
            "weights": selected_train_weights,
            "detailed_labels": selected_train_detailed_labels,
        }
        
        self.__train_df = sampled_df
        self.__train_df["detailed_labels"] = selected_train_detailed_labels
        self.__train_df["labels"] = selected_train_labels
        self.__train_df["weights"] = selected_train_weights
        

        del sampled_df, selected_train_labels, selected_train_weights, selected_train_detailed_labels

        buffer = io.StringIO()
        self.__train_set["data"].info(buf=buffer, memory_usage="deep", verbose=False)
        info_str = "Training Data :\n" + buffer.getvalue()
        logger.debug(info_str)
        logger.info("Train data loaded successfully")

    def load_test_set(self):

        test_data_dir = os.path.join(self.input_dir, "test", "data")

        # read test setting
        test_set = {
            "ztautau": pd.DataFrame(),
            "diboson": pd.DataFrame(),
            "ttbar": pd.DataFrame(),
            "htautau": pd.DataFrame(),
        }

        for key in test_set.keys():

            test_data_path = os.path.join(test_data_dir, f"{key}_data.parquet")
            test_set[key] = pd.read_parquet(test_data_path, engine="pyarrow")

        self.__test_set = test_set

        for key in self.__test_set.keys():
            buffer = io.StringIO()
            self.__test_set[key].info(buf=buffer, memory_usage="deep", verbose=False)
            info_str = str(key) + ":\n" + buffer.getvalue()

            logger.debug(info_str)
            
        logger.info("Test data loaded successfully")  
          
    def merge_test_train(self):
        """
        Merges the train and test datasets into a single DataFrame.
        Returns:
            pd.DataFrame: Merged DataFrame containing both train and test data.
        """
        if self.__train_set is None:
            raise ValueError("Train set is not loaded. Please load the train set first.")
        if self.__test_set is None:
            raise ValueError("Test set is not loaded. Please load the test set first.")
        merged_data = []
        for key in self.__test_set.keys():
            test_data = self.__test_set[key]
            test_data["detailed_labels"] = key
            if key == 'htautau':
                test_data["labels"] = 1
            else:
                test_data["labels"] = 0
            
            merged_data.append(test_data)
            
        merged_data.append(self.__train_df)
        merged_data = pd.concat(merged_data, ignore_index=True)
        
        # We are merging the previous test and train set hence the sum of weights will be double the normal amount.  
        # Hence a normalisation (dived by 2) is needed.
                
        merged_data["weights"] = merged_data["weights"].astype(np.float32) / 2  
        return merged_data

        
        
parser = argparse.ArgumentParser(
    description="This is script to merge csv files together into one."
)
parser.add_argument("--input", "-i", help="Input file location")
parser.add_argument("--output", "-o", help="Output file location")
parser.add_argument(
    "--parquet", "-p", action="store_true", help="Convert merged data to parquet"
)

args = parser.parse_args()
if args.output:
    merged_file_path = Path(args.output)
else:
    if args.parquet:
        merged_file_path = Path.cwd() / "Merged_output.parquet"
    else:
        merged_file_path = Path.cwd() / "Merged_output.csv"

data = Data(args.input)
data.load_train_set()
data.load_test_set()
merged_data = data.merge_test_train()



full_data = DER_data(merged_data)

meta_data = {
    "author": "FAIR Universe",
    "total_rows": len(full_data),
    "total_columns": len(full_data.columns),
    "columns": list(full_data.columns),
    "detailed_labels": full_data["detailed_labels"].unique().tolist(),
    "sum_weights": float(full_data["weights"].sum()),  # Convert to native float
    "luminosity": 10,
}

print (f"Meta data: {meta_data}")

metadata_file_path = merged_file_path.with_suffix('.json')
with open(metadata_file_path, 'w') as f:
    json.dump(meta_data, f, indent=4)
    logger.info(f"Meta data saved to {metadata_file_path}")

from process_counter import to_parquet, to_csv
if args.parquet:
    to_parquet(full_data, merged_file_path)
else:
    to_csv(full_data, merged_file_path)

logger.info(f"Full data saved to {merged_file_path}")

