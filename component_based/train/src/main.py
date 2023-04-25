#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json
import pickle

import pandas as pd
from google.cloud import storage
from kfp.v2.dsl import Metrics, Model
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, train_test_split


def obtain_args():
    """
    Get the args
    """
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--input-dataset", type=str, help="")
    parser.add_argument("--datasplit-seed", type=int, help="")
    parser.add_argument("--selected-features", type=str, help="")  # Json string
    parser.add_argument("--selected-label", type=str, help="")
    parser.add_argument("--my-hyper-params-dict", type=str, help="")  # Json string
    #
    parser.add_argument("--eval-metrics", type=Metrics, help="")
    parser.add_argument("--model", type=Model, help="")
    #
    args = parser.parse_args()

    return args


# Obtain args
args = obtain_args()

# Read table from upstream compnents
print("args.input_dataset", args.input_dataset)
df = pd.read_csv(args.input_dataset)

# Split Features and Labels
X = df[json.loads(args.selected_features)]
assert X.isna().sum().sum() == 0  # NB: not the best practice
y = df[args.selected_label]

# Split the data for train (80%) and validation (20%)
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=args.datasplit_seed
)

# ========================
# Train the model
# ========================
elastic_net_reg = ElasticNet(random_state=42)
# Hyper-param tuning
random_search = RandomizedSearchCV(
    elastic_net_reg,
    param_distributions=json.loads(args.my_hyper_params_dict),
    n_iter=8,
    scoring="neg_mean_squared_error",
    n_jobs=4,
    cv=5,
    verbose=3,
    random_state=1001,
)
random_search.fit(X_train, y_train)
# Get the best
elastic_net_reg_best = random_search.best_estimator_
best_hyperparam = random_search.best_params_

# Get the trained model performance with validation data
y_val_pred = elastic_net_reg_best.predict(X_val)
val_mse = mean_absolute_error(y_val, y_val_pred)
val_mae = mean_squared_error(y_val, y_val_pred)
metrics_dict = {
    "val_mse": val_mse,
    "val_mae": val_mae,
    "best_hyper_param": best_hyperparam,
}

# ========================
# Save the metrics_dict
# ========================
# args.eval_metrics has .path, .name, .metadata, .uri
if not args.eval_metrics.uri.startswith("gs://"):
    save_full_path = args.eval_metrics.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.eval_metrics.uri

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

with open(file_name, "w") as f:
    json.dump(metrics_dict, f)

blob.upload_from_filename(file_name)

# ========================
# Save the model
# ========================
# NB: Apr-2023, joblib file had problem to deploy on endpoint
# NB: Model path should end model.pkl or model.joblib (i.e., model.path)
# https://cloud.google.com/vertex-ai/docs/training/exporting-model-artifacts#pickle_1
# import joblib; joblib.dump(elastic_net_reg_best, f"{model.path}.joblib")
if not args.model.uri.startswith("gs://"):
    save_full_path = args.model.name.replace("/gcs/", "gs://")
else:
    save_full_path = args.model.uri
print("save_full_path", save_full_path)

# /PROJECT_NUM/PIPELINE_NAME/COMPONENT/artefact part for blob
blob_name = "/".join(save_full_path.split("/")[3:])
file_name = save_full_path.split("/")[-1]
# upload file to the target GCS
blob = bucket.blob(f"{blob_name}.pkl")

with open(f"{file_name}.pkl", "wb") as f:
    pickle.dump(elastic_net_reg_best, f)
blob.upload_from_filename(f"{file_name}.pkl")

# return (val_mse, val_mae, best_hyperparam)
