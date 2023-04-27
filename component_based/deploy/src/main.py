#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import os

import gcsfs
from google.cloud import aiplatform
from kfp.v2.dsl import Model


def run(
    project_id: str,
    model: str,
    serving_container_image_uri: str,
    endpoint_machine_type: str,
    endpoint_model_name: str,
    vertex_endpoint_uri: str,
    vertex_model_uri: str,
) -> None:
    # ========================
    # Deploy model
    # ========================
    # Instantiate ai-platfom client
    aiplatform.init(project=project_id)
    # List of pre-build docker images:
    # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
    # https://aiinpractice.com/gcp-mlops-vertex-ai-pipeline-scikit-learn/
    # NB: using the base image, and this must be model.joblib or model.pkl
    deployed_model = aiplatform.Model.upload(
        display_name=endpoint_model_name,
        artifact_uri=os.path.dirname(model.name),
        serving_container_image_uri=serving_container_image_uri,
    )
    endpoint = deployed_model.deploy(machine_type=endpoint_machine_type)

    # ======================
    # Save the endpoint and model information
    # NB: both of them are defined as "String" object, so
    #     no .name
    # ======================
    gcs_fs = gcsfs.GCSFileSystem()
    #
    vertex_endpoint_uri_path = vertex_endpoint_uri.replace("/gcs/", "gs://")
    with gcs_fs.open(vertex_endpoint_uri_path, "w") as f:
        f.write(endpoint.resource_name)
    #
    vertex_model_uri_path = vertex_model_uri.replace("/gcs/", "gs://")
    with gcs_fs.open(vertex_model_uri_path, "w") as f:
        f.write(deployed_model.resource_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--project-id", type=str, help="")
    parser.add_argument("--model", type=Model, help="")
    parser.add_argument("--serving-container-image-uri", type=str, help="")
    parser.add_argument("--endpoint-machine-type", type=str, help="")
    parser.add_argument("--endpoint-model-name", type=str, help="")
    #
    parser.add_argument("--vertex-endpoint-uri", type=str, help="")
    parser.add_argument("--vertex-model-uri", type=str, help="")
    #
    args = parser.parse_args()

    run(**vars(args))
