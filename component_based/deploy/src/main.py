#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json
import os

from google.cloud import aiplatform, storage
from kfp.v2.dsl import Artifact, Model


def obtain_args():
    """
    Get the args
    """
    parser = argparse.ArgumentParser(description="")
    #
    parser.add_argument("--project-id", type=str, help="")
    parser.add_argument("--model", type=Model, help="")
    parser.add_argument("--serving-container-image-uri", type=str, help="")
    parser.add_argument("--endpoint-machine-type", type=str, help="")
    parser.add_argument("--endpoint-model-name", type=str, help="")
    parser.add_argument("--model-deployment-flag", type=Artifact, help="")
    #
    parser.add_argument("--deployment-info", type=Artifact, help="")
    parser.add_argument("--vertex-endpoint-uri", type=str, help="")
    parser.add_argument("--vertex-model-uri", type=str, help="")
    #
    args = parser.parse_args()

    return args


# Obtain args
args = obtain_args()

# Get the flag value from upstream components
with open(args.model_deployment_flag.name, "r") as f:
    str_flag = f.readline()
model_deployment_flag_json = json.loads(str_flag)

if not model_deployment_flag_json["model_eval_passed"]:
    print("Model failed to pass the threshold")

else:
    # ========================
    # Deploy model
    # ========================
    # Instantiate ai-platfom client
    aiplatform.init(project=args.project_id)
    # List of pre-build docker images:
    # https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers
    # https://aiinpractice.com/gcp-mlops-vertex-ai-pipeline-scikit-learn/
    # NB: using the base image, and this must be model.joblib or model.pkl
    deployed_model = aiplatform.Model.upload(
        display_name=args.endpoint_model_name,
        artifact_uri=os.path.dirname(args.model.name),
        serving_container_image_uri=args.serving_container_image_uri,
    )
    endpoint = deployed_model.deploy(machine_type=args.endpoint_machine_type)

    # ========================
    # Save the deployment_info
    # ========================
    # args.model_deployment_flag has .path, .name, .metadata, .uri
    if not args.deployment_info.uri.startswith("gs://"):
        save_full_path = args.deployment_info.name.replace("/gcs/", "gs://")
    else:
        save_full_path = args.deployment_info.uri

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

    metrics_dict = {
        "vertex_endpoint_uri": endpoint.resource_name,
        "vertex_model_uri": deployed_model.resource_name,
    }

    with open(file_name, "w") as f:
        json.dump(metrics_dict, f)
    blob.upload_from_filename(file_name)

    # Save the endponit and model information
    with open(args.vertex_endpoint_uri, "w") as f:
        f.write(endpoint.resource_name)
    with open(args.vertex_model_uri, "w") as f:
        f.write(deployed_model.resource_name)
