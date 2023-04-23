#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
from kfp.v2.dsl import Dataset

import pandas as pd
import io
import google.cloud.storage as storage

parser = argparse.ArgumentParser(description="")

parser.add_argument("--project-id", type=str, help="")
parser.add_argument("--original-bucket-id", type=str, help="")
parser.add_argument("--target-filename", type=str, help="")
#
parser.add_argument("--output-dataset", type=Dataset, help="")
args = parser.parse_args()

# ===============================
#  Collect data from storage
# ===============================
# Instantiates a client
storage_client = storage.Client()
bucket = storage_client.bucket(args.original_bucket_id)

# Download csv file from GCS
blob = bucket.blob(args.target_filename)  # train.csv or test.csv
data = blob.download_as_string()
df = pd.read_csv(io.BytesIO(data))

# ===============================
#  Some feature engineering
#  1. Mean fill + creating ratio
# ===============================
# Get mean value for the target column
mean_target_col = df["TotalBsmtSF"].mean()
# Replace 0 value to mean
df["TotalBsmtSF_fillmean"] = df["TotalBsmtSF"].replace(0, mean_target_col)
# Get mean value for the target column
mean_target_col = df["BsmtUnfSF"].mean()
# Replace 0 value to mean
df["BsmtUnfSF_fillmean"] = df["BsmtUnfSF"].replace(0, mean_target_col)
df["BsmtUnfSF_TotalBsmtSF_ratio"] = (
    df["BsmtUnfSF_fillmean"] / df["TotalBsmtSF_fillmean"]
)

# Create an output
df.to_csv(args.output_dataset.path, index=False, header=True)

print(df.shape)
