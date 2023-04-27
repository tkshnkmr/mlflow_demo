"""
Preprocessing code for ML pipeline
"""

import argparse

import pandas as pd
from kfp.v2.dsl import Dataset


def run(
    original_bucket_id: str, target_filename: str, output_dataset: str
) -> None:
    """
    Main part of preprocessing
    """
    # ===============================
    #  Collect data from storage
    # ===============================
    """
    NB: We can use storage client for the process, but if the file is small,
        directly read and write data to gcs works correctly
    # Instantiates a client
    storage_client = storage.Client()
    bucket = storage_client.bucket(original_bucket_id)
    # Download csv file from GCS
    blob = bucket.blob(target_filename)  # train.csv or test.csv
    data = blob.download_as_string()
    df = pd.read_csv(io.BytesIO(data))
    """
    df = pd.read_csv(f"gs://{original_bucket_id}/{target_filename}")

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
    print("Dataframe shape:", df.shape)

    # Save the dataframe
    output_dataset_ = output_dataset.name.replace("/gcs/", "gs://")
    # NB: If we explicitly mention ***.csv to add extention, the metadata store
    #     doesn't know follow the lineage
    # df.to_csv(f"{output_dataset_}/{target_filename}", index=False, header=True)
    df.to_csv(output_dataset_, index=False, header=True)
    print(f"Save processed data at: {output_dataset_}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--original-bucket-id", type=str, help="")
    parser.add_argument("--target-filename", type=str, help="")
    #
    parser.add_argument("--output-dataset", type=Dataset, help="")
    args = parser.parse_args()

    run(**vars(args))
