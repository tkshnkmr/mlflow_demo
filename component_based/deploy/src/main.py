#!/usr/bin/env/python3
"""
yaml file based to implement pipeline components
"""

import argparse
import json
import os

from google.cloud import aiplatform
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
    parser.add_argument("--vertex-endpoint", type=Artifact, help="")
    parser.add_argument("--vertex-model", type=Model, help="")
    #
    args = parser.parse_args()

    return args


# Obtain args
args = obtain_args()

# Get the flag value from upstream components
with open(args.model_deployment_flag.name, "r") as f:
    str_flag = f.readline()
model_deployment_flag_json = json.loads(str_flag)
print("model_deployment_flag_json", model_deployment_flag_json)

if not model_deployment_flag_json["model_eval_passed"]:
    print("Model failed to pass the threshold")

else:
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

    print("endpoint", endpoint)
    print("endpoint.resource_name", endpoint.resource_name)

    print("deployed_model", deployed_model)
    print("deployed_model.resource_name", deployed_model.resource_name)

    # Save data to the output params
    args.vertex_endpoint.uri = endpoint.resource_name
    args.vertex_model.uri = deployed_model.resource_name
