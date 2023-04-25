#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json
import pickle

import pandas as pd
import numpy as np
from google.cloud import storage
from kfp.v2.dsl import Dataset, Artifact, Model


def obtain_args():
    """
    Get the args
    """
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--input-dataset", type=str, help="")
    parser.add_argument("--selected-features", type=str, help="")  # Json string
    parser.add_argument("--model", type=Model, help="")
    #
    parser.add_argument("--pred-output-csv", type=Dataset, help="")
    parser.add_argument("--model-deployment-flag", type=Artifact, help="")
    #
    args = parser.parse_args()

    return args


# Obtain args
args = obtain_args()

# load the test data
print("args.input_dataset", args.input_dataset)
df = pd.read_csv(args.input_dataset)

# Split Features and Labels
X = df[json.loads(args.selected_features)]
X.dropna(inplace=True)  # NB: not the best practice
assert X.isna().sum().sum() == 0  # NB: not the best practice

# ==========================
# Download the model file
# ==========================
# save_full_path must be "gs://BUCKET_NAME/PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact"
# args.model has .path, .name, .metadata, .uri
if not args.model.uri.startswith("gs://"):
    save_full_path = args.model.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.model.uri

bucket_name = save_full_path.split("/")[2]
# /PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact part for blob
blob_name = "/".join(save_full_path.split("/")[3:])
file_name = save_full_path.split("/")[-1]

# Instantiates a client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
# download file to the target GCS
blob = bucket.blob(f"{blob_name}.pkl")
blob.download_to_filename(f"{file_name}.pkl")

# elastic_net_reg = pickle.load(f"{model.path}.pkl")
with open(f"{file_name}.pkl", "rb") as f:
    elastic_net_reg = pickle.load(f)

# Prediction towards to test data
y_test_pred = elastic_net_reg.predict(X)

# ========================
# Save the pred_output_csv
# ========================
# args.pred_output_csv has .path, .name, .metadata, .uri
if not args.pred_output_csv.uri.startswith("gs://"):
    save_full_path = args.pred_output_csv.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.pred_output_csv.uri

# save_full_path must be "gs://BUCKET_NAME/PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact"
bucket_name = save_full_path.split("/")[2]
# /PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact part for blob
blob_name = "/".join(save_full_path.split("/")[3:])
file_name = save_full_path.split("/")[-1]

# Instantiates a client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
# upload file to the target GCS
blob = bucket.blob(blob_name)

np.savetxt(file_name, y_test_pred.round(1), delimiter=",")
blob.upload_from_filename(file_name)

# ========================
# Save the model_deployment_flag
# ========================
# args.model_deployment_flag has .path, .name, .metadata, .uri
if not args.model_deployment_flag.uri.startswith("gs://"):
    save_full_path = args.model_deployment_flag.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.model_deployment_flag.uri

# save_full_path must be "gs://BUCKET_NAME/PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact"
bucket_name = save_full_path.split("/")[2]
# /PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact part for blob
blob_name = "/".join(save_full_path.split("/")[3:])
file_name = save_full_path.split("/")[-1]

# Instantiates a client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
# upload file to the target GCS
blob = bucket.blob(blob_name)

# dumping metrics_dict
score = 4678  # NB: RANDOM number for demo
metrics_dict = {"model_eval_passed": True, "threshould_or_score": score}

with open(file_name, "w") as f:
    json.dump(metrics_dict, f)
blob.upload_from_filename(file_name)
