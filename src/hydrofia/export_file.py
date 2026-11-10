import pandas as pd

def write_export_file(data: pd.DataFrame, path):
    data.to_csv(path, index=False, sep="\t")
