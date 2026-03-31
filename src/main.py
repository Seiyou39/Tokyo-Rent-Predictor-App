from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import json

app = FastAPI()

# 1. Input the trained model
model = joblib.load("artifacts/model.pkl")

# 2. Read the columns order used in training the model
with open("artifacts/columns.json", "r", encoding="utf-8") as f:
    feature_columns = json.load(f)

# 3. Read the standardization parameters
scaler_df = pd.read_csv("data/processed/scaler_info.csv", index_col=0)


# 4. User input data model
class HouseInput(BaseModel):
    area: float
    walk: float
    age: float
    floor: float
    rooms: float
    ward: str
    layout_type: str


# 5. Convert user input to the DataFrame format needed by the model
def build_input(data: HouseInput) -> pd.DataFrame:
    row = {col: 0 for col in feature_columns}

    # fill in the feature values
    if "area" in row:
        row["area"] = data.area
    if "walk" in row:
        row["walk"] = data.walk
    if "age" in row:
        row["age"] = data.age
    if "floor" in row:
        row["floor"] = data.floor
    if "rooms" in row:
        row["rooms"] = data.rooms

    # 6. one-hot columns
    ward_col = f"ward_{data.ward}"
    layout_col = f"layout_type_{data.layout_type}"

    if ward_col in row:
        row[ward_col] = 1
    if layout_col in row:
        row[layout_col] = 1

    return pd.DataFrame([row], columns=feature_columns)


# 7. Standardization function
def standardize(df: pd.DataFrame, scaler_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in scaler_df.index:
        mean = scaler_df.loc[col, "mean"]
        std = scaler_df.loc[col, "std"]

        if col in df.columns:
            if std != 0:
                df[col] = (df[col] - mean) / std
            else:
                df[col] = 0

    return df

# 8. API Test
@app.get("/")
def root():
    return {"message": "Rent prediction API is running"}

# 9. API Prediction
@app.post("/predict")
def predict(data: HouseInput):
    X_input = build_input(data)
    X_input = standardize(X_input, scaler_df)

    pred = model.predict(X_input)[0]

    return {"predicted_rent": float(pred)}