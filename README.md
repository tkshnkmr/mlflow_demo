# Demo of Kubeflow pipeline on GCP

## Overview
Two kubeflow pipeline examples:

1. Notebook based, standalone python solution.

    Main file: ``` kubeflow_gcp_from_notebook.ipynb ```

2. Container based, solution.

    Main file: ``` kubeflow_gcp_from_components.ipynb ```
    Components: ``` component_based/ ```

## Pre-requisite
1. Setup Python environtment (Python3.10.10)
    ```console
    python3 -m venv ~/YOUR_PY_ENV
    source ~/YOUR_PY_ENV/bin/activate
    ```
2. Install required packages (inc. ``` kfp ```)

3. Setup environment variables inc. 
    
    NB: Credentials file can be created and downloaded from your GCP console

    ```console
    export $PROJECT_ID
    export $GOOGLE_APPLICATION_CREDENTIALS
    ```

4. Setup service account on your GCP console

## Pipeline overview
![image info](./pipeline_overview.png)
