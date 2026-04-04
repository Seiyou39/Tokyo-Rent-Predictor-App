import joblib
import pandas as pd
import json
from src.features.onehot_encoder import encoder_transform
from src.features.scaler import scaler_transform

# 1. Load the trained model
model = joblib.load("models/model.pkl")

with open("models/columns.json", "r") as f:
    feature_columns = json.load(f)

scaler_df = pd.read_csv("models/scaler_info.csv", index_col=0).to_dict(orient="index")


def predict_single(data: dict):
    df = pd.DataFrame([data])
    df = encoder_transform(df, feature_columns)
    df = scaler_transform(df, scaler_df)
    pred = model.predict(df)[0]
    return float(pred)