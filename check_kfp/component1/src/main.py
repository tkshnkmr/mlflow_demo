#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import json
import argparse
from kfp.v2.dsl import Dataset, Model, Metrics, Artifact
from google.cloud import storage

def obtain_args():
    """
    Get the args, see https://kubeflow-pipelines.readthedocs.io/en/2.0.0b15/source/dsl.html
    """

    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--in-str", type=str, help="")
    parser.add_argument("--in-int", type=int, help="")
    parser.add_argument("--in-float", type=float, help="")
    #
    parser.add_argument("--out-artifact", type=Artifact, help="")  #name, uri, metadata
    parser.add_argument("--out-dataset", type=Dataset, help="")  #name, uri, metadata
    parser.add_argument("--out-metrics", type=Metrics, help="")  #name, uri, metadata
    parser.add_argument("--out-model", type=Model, help="")  #name, uri, metadata
    #
    parser.add_argument("--out-artifact-path", type=Artifact, help="")  #name, uri, metadata
    parser.add_argument("--out-dataset-path", type=Dataset, help="")  #name, uri, metadata
    parser.add_argument("--out-metrics-path", type=Metrics, help="")  #name, uri, metadata
    parser.add_argument("--out-model-path", type=Model, help="")  #name, uri, metadata
    # 
    args = parser.parse_args()
    return args


# Obtain args
args = obtain_args()

print("args.in_str", args.in_str)
print("args.in_int", args.in_int)
print("args.in_float", args.in_float)

# regardless output defined in yaml file, path=None, metadata={}, url=''
# name=/gcs/BUCKET_NAME/PROJECT_NUM/PIPELINE_NAME/COMPONENT_NAME/variable_name
print("args.out_artifact.path", args.out_artifact.path)
print("args.out_artifact.uri", args.out_artifact.uri)
print("args.out_artifact.metadata", args.out_artifact.metadata)
# 
print("args.out_artifact.name", args.out_artifact.name)
print("args.out_dataset.name", args.out_dataset.name)
print("args.out_metrics.name", args.out_metrics.name)
print("args.out_model.name", args.out_model.name)
# 
print("args.out_artifact_path.name", args.out_artifact_path.name)
print("args.out_dataset_path.name", args.out_dataset_path.name)
print("args.out_metrics_path.name", args.out_metrics_path.name)
print("args.out_model_path.name", args.out_model_path.name)

# # Doesn't work
# args.out_artifact = "1"
# args.out_dataset = {"1": "10"}
# args.out_metrics = {"1": 0.1}
# args.out_model = {"ABC": 123}

# 
save_full_path = args.out_artifact.name.replace("/gcs/", "gs://")
bucket_name = save_full_path.split("/")[2]
blob_name = "/".join(save_full_path.split("/")[3:])
file_name = save_full_path.split("/")[-1]
with open(file_name, "w") as f:
    f.write("10")

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)
blob.upload_from_filename(file_name)

with open(args.out_dataset.name, "w") as f:
    json.dump({"1": "10"}, f)

with open(args.out_artifact_path.name, "w") as f:
    f.write("args.out_artifact_path.name")
with open(args.out_dataset_path.name, "w") as f:
    json.dump({"args.out_artifact_path.name": "12345678"}, f)


with open(args.out_metrics.name, "w") as f:
    f.write("args.out_metrics.name")
with open(args.out_metrics_path.name, "w") as f:
    json.dump({"args.out_metrics_path.name": "12345678"}, f)

with open(args.out_model.name, "w") as f:
    f.write("args.out_model.name")
with open(args.out_model.name, "w") as f:
    json.dump({"args.out_model_path.name": "12345678"}, f)

# # ===============================
# #  Collect data from storage
# # ===============================
# # Instantiates a client
# storage_client = storage.Client()
# bucket = storage_client.bucket(args.original_bucket_id)

# # Download csv file from GCS
# blob = bucket.blob(args.target_filename)  # train.csv or test.csv
# data = blob.download_as_string()
# df = pd.read_csv(io.BytesIO(data))

# # ===============================
# #  Some feature engineering
# #  1. Mean fill + creating ratio
# # ===============================
# # Get mean value for the target column
# mean_target_col = df["TotalBsmtSF"].mean()
# # Replace 0 value to mean
# df["TotalBsmtSF_fillmean"] = df["TotalBsmtSF"].replace(0, mean_target_col)
# # Get mean value for the target column
# mean_target_col = df["BsmtUnfSF"].mean()
# # Replace 0 value to mean
# df["BsmtUnfSF_fillmean"] = df["BsmtUnfSF"].replace(0, mean_target_col)
# df["BsmtUnfSF_TotalBsmtSF_ratio"] = (
#     df["BsmtUnfSF_fillmean"] / df["TotalBsmtSF_fillmean"]
# )

# # args.output_dataset has .path, .name, .metadata, and .uri
# # Save model and weights
# if not args.output_dataset.uri.startswith("gs://"):
#     save_full_path = args.output_dataset.name.replace("/gcs/", "gs://")
# else:
#     save_full_path = args.output_dataset.uri
# print("save_full_path", save_full_path)
# df.to_csv(save_full_path, index=False, header=True)
