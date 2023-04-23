#!/bin/bash -e

image_name=gcr.io/$PROJECT_ID/sample_preprocessing
image_tag=latest
full_image_name=${image_name}:${image_tag}

cd "$(dirname "$0")"

docker build --platform=linux/amd64 -t "$full_image_name" .
docker push "$full_image_name"