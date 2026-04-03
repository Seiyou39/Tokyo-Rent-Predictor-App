import pandas as pd

def fit_encoder(df, cols):
    df_encoded = pd.get_dummies(df, columns=cols)
    columns = df_encoded.columns.tolist()
    return columns

def encoder_transform(df, columns):
    df_encoded = pd.get_dummies(df, columns=["location", "layout"])

    # add missing columns with default value 0
    for col in columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # keep the same column order as the training data
    df_encoded = df_encoded[columns]

    return df_encoded