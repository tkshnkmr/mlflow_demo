"""
Preprocess data for ml model
"""
import pandas as pd
from load import load_my_data


def preprocess_my_data(df) -> pd.DataFrame:
    """
    Some preprocessing
    """
    # Create a new feature
    df['AveRooms_bin'] = pd.to_numeric(pd.cut(x = df['AveRooms'], 
                            bins = [0, 3, 5, 7, 10, 300], 
                            labels = [1, 2, 3, 4, 5]
                            ))

    return df


# df = load_my_data()
# df = preprocess_my_data()