import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from src.features.onehot_encoder import fit_encoder, encoder_transform
from src.features.scaler import fit_scaler, scaler_transform
import numpy as np
import joblib
import json

# 1. read data
df = pd.read_csv("data/processed/2026-04-02_data/clean_data.csv")

'''debug
print(df[df.isna().any(axis=1)])
print(df.isna().sum()[df.isna().sum() > 0])
nan_cols = df.columns[df.isna().any()]
print(df.loc[df.isna().any(axis=1), nan_cols])
'''

# 2. split data into features (X) and target (y)
X = df.drop(columns=["rent"])
y = df["rent"]

# 3. split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=39
)

# 4. create a linear regression model
model = LinearRegression()

num_cols = ["walk", "age", "total_floors", "floor", "area"]
feature_columns = fit_encoder(X_train, ["location", "layout"])
scaler_info = fit_scaler(X_train, num_cols)

X_train = scaler_transform(X_train, scaler_info)
X_test = scaler_transform(X_test, scaler_info)
X_train = encoder_transform(X_train, feature_columns)
X_test = encoder_transform(X_test, feature_columns)

# 5. learning
model.fit(X_train, y_train)

# 6. predict
y_pred = model.predict(X_test)

# 7. evaluate the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

coef_df = pd.DataFrame({
    "feature": X_train.columns,
    "weight": model.coef_
})

coef_df["abs"] = coef_df["weight"].abs()
print(coef_df.sort_values(by="abs", ascending=False))

print("MSE :", mse)
print("RMSE:", rmse)
print("R2  :", r2)


# 8. save the columns order
scaler_df = pd.DataFrame(scaler_info).T
scaler_df.to_csv("models/scaler_info.csv")

with open("models/columns.json", "w", encoding="utf-8") as g:
    json.dump(feature_columns, g, ensure_ascii=False, indent=2)

# 9. save the model
joblib.dump(model, "models/model.pkl")
