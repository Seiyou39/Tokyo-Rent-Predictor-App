import pandas as pd

#read the data
df = pd.read_csv("data/raw/Data.csv")

#select the columns we need and drop rows with missing values in those columns
df = df.loc[:, :"area"]
df = df.dropna(subset=["ward", "walk", "age", "floor", "rent", "type", "area"])

#divide the type column into two columns, one for the number of rooms and one for the layout type
df["rooms"] = df["type"].str.extract(r'(\d+)')
df["layout_type"] = df["type"].str.extract(r'([A-Za-z]+)')[0].str.upper()

#drop the original type column
df = df.drop(columns=["type"])

# one-hot encoding
df_encoded = pd.get_dummies(df, columns=["ward", "layout_type"])

# convert boolean columns to integers
for col in df_encoded.columns:
    if df_encoded[col].dtype == "bool":
        df_encoded[col] = df_encoded[col].astype(int)

# feature standardization
feature_cols = ["walk", "age", "area", "rooms", "floor"]
# convert feature columns to numeric, coercing errors to NaN
for col in feature_cols:
    df_encoded[col] = pd.to_numeric(df_encoded[col], errors="coerce")

scaler_info = {}
df_std = df_encoded.copy()
for col in feature_cols:
    mean = df_std[col].mean()
    std = df_std[col].std()

    scaler_info[col] = {"mean": mean, "std": std}

    if std != 0:
        df_std[col] = (df_encoded[col] - mean) / std
    else:
        df_std[col] = 0

df_scaler_info = pd.DataFrame(scaler_info).T

# save data
df_std.to_csv("data/processed/processed_data.csv", index=False)
df_scaler_info.to_csv("data/processed/scaler_info.csv")