#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json

from kfp.v2.dsl import Dataset, Model, Metrics, Artifact
from google.cloud import storage


def obtain_args():
    """
    Get the args
    """

    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--in-artifact-path", type=Artifact, help="")  #name, uri, metadata
    parser.add_argument("--in-dataset-path", type=Dataset, help="")  #name, uri, metadata
    parser.add_argument("--in-metrics-path", type=Metrics, help="")  #name, uri, metadata
    parser.add_argument("--in-model-path", type=Model, help="")  #name, uri, metadata
    # parser.add_argument("--out-metrics", type=str, help="")
    # parser.add_argument("--out-artifact", type=str, help="")
    # 
    parser.add_argument("--output-metadata", type=str, help="")  #name, uri, metadata
    parser.add_argument("--output-model", type=Model, help="")  #name, uri, metadata
    # 
    args = parser.parse_args()
    return args


# Obtain args
args = obtain_args()

# 
print("args.in_artifact_path.name", args.in_artifact_path.name)
print("args.in_dataset_path.name", args.in_dataset_path.name)
print("args.in_metrics_path.name", args.in_metrics_path.name)
print("args.in_model_path.name", args.in_model_path.name)
# 
# print("args.out_artifact.name", args.out_artifact.name)
# print("args.out_artifact.path", args.out_artifact.path)
# print("args.out_artifact.uri", args.out_artifact.uri)
# 
print("args.output_metadata", args.output_metadata)

print("args.output_model.name", args.output_model.name)
print("args.output_model.path", args.output_model.path)
print("args.output_model.uri", args.output_model.uri)

"""
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

# args.output_dataset has .path, .name, .metadata, and .uri
# Save model and weights
if not args.output_dataset.uri.startswith("gs://"):
    save_full_path = args.output_dataset.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.output_dataset.uri
print("save_full_path", save_full_path)
df.to_csv(save_full_path, index=False, header=True)
"""