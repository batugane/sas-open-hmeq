import pandas as pd

def load_data(path):
    """Reads CSV and returns a DataFrame."""
    return pd.read_csv(path, sep=",")
