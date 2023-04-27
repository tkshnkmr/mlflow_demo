"""
Model training code for ML pipeline
"""

import argparse
import json
import pickle

import gcsfs
import pandas as pd
from kfp.v2.dsl import Artifact, Metrics, Model
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, train_test_split


def run(
    input_dataset: str,
    datasplit_seed: int,
    selected_features: str,
    selected_label: str,
    my_hyper_params_dict: str,
    eval_metrics: str,
    model: str,
    best_hyperparam: str,
) -> None:
    """
    Main part of training
    """
    # Read table from upstream compnents
    df = pd.read_csv(input_dataset)
    print("Loaded data from input_dataset", input_dataset)

    # Split Features and Labels
    X = df[json.loads(selected_features)]
    assert X.isna().sum().sum() == 0  # NB: not the best practice
    y = df[selected_label]

    # Split the data for train (80%) and validation (20%)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=datasplit_seed
    )

    # ========================
    # Train the model
    # ========================
    elastic_net_reg = ElasticNet(random_state=42)
    # Hyper-param tuning
    random_search = RandomizedSearchCV(
        elastic_net_reg,
        param_distributions=json.loads(my_hyper_params_dict),
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
    model_hyperparam_best = random_search.best_params_

    # Get the trained model performance with validation data
    y_val_pred = elastic_net_reg_best.predict(X_val)
    val_mse = mean_absolute_error(y_val, y_val_pred)
    val_mae = mean_squared_error(y_val, y_val_pred)
    metrics_dict = {
        "val_mse": val_mse,
        "val_mae": val_mae,
        "best_hyperparam": model_hyperparam_best,
    }

    # ========================
    # Save the metrics_dict
    # ========================
    """
    # NB: We are not able to save the file on the empty dir on GCS, i.e.
    #     either 1) use storage.Client() & blob.upload_from_filename()
    #     or,    2) use gcsfs
    """
    gcs_fs = gcsfs.GCSFileSystem()
    eval_metrics_path = eval_metrics.name.replace("/gcs/", "gs://")
    with gcs_fs.open(eval_metrics_path, "w") as f:
        json.dump(metrics_dict, f)
    print(f"Save the metrics file at: {eval_metrics_path}")

    best_hyperparam_path = best_hyperparam.name.replace("/gcs/", "gs://")
    with gcs_fs.open(best_hyperparam_path, "w") as f:
        json.dump(model_hyperparam_best, f)
    print(f"Save the best hyperparam file at: {best_hyperparam_path}")

    # ========================
    # Save the model
    # ========================
    # NB: Apr-2023, joblib file had problem to deploy on endpoint
    # NB: Model path should end model.pkl or model.joblib (i.e., model.path)
    # https://cloud.google.com/vertex-ai/docs/training/exporting-model-artifacts#pickle_1
    # import joblib; joblib.dump(elastic_net_reg_best, f"{model.path}.joblib")
    model_path = model.name.replace("/gcs/", "gs://")
    with gcs_fs.open(f"{model_path}.pkl", "wb") as f:
        pickle.dump(elastic_net_reg_best, f)
    print(f"Save the model file at: {eval_metrics_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--input-dataset", type=str, help="")
    parser.add_argument("--datasplit-seed", type=int, help="")
    parser.add_argument("--selected-features", type=str, help="")
    parser.add_argument("--selected-label", type=str, help="")
    parser.add_argument("--my-hyper-params-dict", type=str, help="")
    #
    parser.add_argument("--eval-metrics", type=Metrics, help="")
    parser.add_argument("--model", type=Model, help="")
    parser.add_argument("--best-hyperparam", type=Artifact, help="")
    #
    args = parser.parse_args()

    run(**vars(args))
