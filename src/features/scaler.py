import pandas as pd

def fit_scaler(df, cols):
    scaler_info = {}

    for col in cols:
        mean = df[col].mean()
        std = df[col].std()

        scaler_info[col] = {"mean": mean, "std": std}

    return scaler_info


def scaler_transform(df, scaler_info):
    df = df.copy()

    for col in scaler_info:
        mean = scaler_info[col]["mean"]
        std = scaler_info[col]["std"]

        if std != 0:
            df[col] = (df[col] - mean) / std
        else:
            df[col] = 0

    return df