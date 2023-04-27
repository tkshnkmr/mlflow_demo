#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json
import pickle

import gcsfs
import pandas as pd
from kfp.v2.dsl import Artifact, Dataset, Model


def run(
    input_dataset: str,
    selected_features: str,
    model: str,
    pred_output_csv: str,
    model_deployment_flag: str,
) -> None:
    """
    Main part of evaluation
    """
    # load the test data
    df = pd.read_csv(input_dataset)
    print("Loaded data from input_dataset", input_dataset)

    # Split Features and Labels
    X = df[json.loads(selected_features)]
    X.dropna(inplace=True)  # NB: not the best practice
    assert X.isna().sum().sum() == 0  # NB: not the best practice

    # ==========================
    # Download the model file
    # ==========================
    gcs_fs = gcsfs.GCSFileSystem()
    model_path = model.name.replace("/gcs/", "gs://")
    with gcs_fs.open(f"{model_path}.pkl", "rb") as f:
        elastic_net_reg = pickle.load(f)
    print(f"Loaded the model file from: {model_path}")

    # Prediction towards to test data
    y_test_pred = elastic_net_reg.predict(X)

    # ========================
    # Save the pred_output_csv
    # ========================
    pred_output_csv_path = pred_output_csv.name.replace("/gcs/", "gs://")
    pd.DataFrame(y_test_pred).to_csv(pred_output_csv_path, index=False, header=False)
    print(f"Save the prediction file at: {pred_output_csv_path}")

    # ========================
    # Save the model_deployment_flag
    # ========================
    model_deployment_flag_path = model_deployment_flag.name.replace("/gcs/", "gs://")
    # NB: Should be used Boolean, not string "true"
    with gcs_fs.open(model_deployment_flag_path, "w") as f:
        f.write("true")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--input-dataset", type=str, help="")
    parser.add_argument("--selected-features", type=str, help="")
    parser.add_argument("--model", type=Model, help="")
    #
    parser.add_argument("--pred-output-csv", type=Dataset, help="")
    parser.add_argument("--model-deployment-flag", type=Artifact, help="")
    #
    args = parser.parse_args()

    run(**vars(args))
