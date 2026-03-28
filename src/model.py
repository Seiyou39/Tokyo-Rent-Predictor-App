import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# 1. read data
df = pd.read_csv("data/processed/processed_data.csv")

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
    X, y, test_size=0.2, random_state=42
)

# 4. create a linear regression model
model = LinearRegression()

# 5. learning
model.fit(X_train, y_train)

# 6. predict
y_pred = model.predict(X_test)

# 7. evaluate the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

coef_df = pd.DataFrame({
    "feature": X.columns,
    "weight": model.coef_
})

coef_df["abs"] = coef_df["weight"].abs()
print(coef_df.sort_values(by="abs", ascending=False))

print("MSE :", mse)
print("RMSE:", rmse)
print("R2  :", r2)