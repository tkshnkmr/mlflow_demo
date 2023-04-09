"""
Load data from target resources
"""

import pandas as pd
from sklearn.datasets import fetch_california_housing


# Function to return the orignal data
def load_my_data():
    # Load data
    cal_data = fetch_california_housing(as_frame=True)
    df = cal_data.frame

    # In reality, the data load process would be
    # requests, or pulling data from data warehouse
    # df = pd.read_csv(f"{loc}/{tablename}")

    return df

# df = load_my_data()
