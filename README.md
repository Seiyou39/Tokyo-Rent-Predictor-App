# Tokyo Rent Predictor App

---

## English

### Overview
Tokyo Rent Predictor App is a machine-learning project that predicts apartment rent in Tokyo from property features.  
This repository includes the full workflow: preprocessing raw data, training a regression model, and serving online predictions with FastAPI.

### Features
- **Data preprocessing** (`src/preprocess.py`)
  - Load raw CSV data
  - Handle missing values
  - Split `type` into `rooms` and `layout_type`
  - One-hot encode categorical features
  - Standardize numeric features and save scaler info
- **Model training** (`src/train.py`)
  - Train/test split (`test_size=0.2`, `random_state=42`)
  - Train `LinearRegression`
  - Evaluate with MSE, RMSE, and R²
  - Save artifacts to `artifacts/model.pkl` and `artifacts/columns.json`
- **API serving** (`src/main.py`)
  - `GET /` health endpoint
  - `POST /predict` prediction endpoint

### Project Structure
```text
Tokyo-Rent-Predictor-App/
├─ src/
│  ├─ preprocess.py
│  ├─ train.py
│  └─ main.py
├─ data/
│  ├─ raw/
│  │  └─ Data.csv
│  └─ processed/
│     ├─ processed_data.csv
│     └─ scaler_info.csv
└─ artifacts/
   ├─ model.pkl
   └─ columns.json
```

### Requirements
- Python 3.10+
- Recommended install:

```bash
pip install fastapi uvicorn pandas scikit-learn numpy joblib pydantic
```

### Quick Start
1. Preprocess data:
```bash
python src/preprocess.py
```
2. Train model:
```bash
python src/train.py
```
3. Run API:
```bash
uvicorn src.main:app --reload
```
4. Open docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API
- `GET /`
  - Response:
```json
{"message": "Rent prediction API is running"}
```

- `POST /predict`
  - Request:
```json
{
  "area": 25.5,
  "walk": 8,
  "age": 12,
  "floor": 3,
  "rooms": 1,
  "ward": "Shinjuku",
  "layout_type": "K"
}
```
  - Response:
```json
{
  "predicted_rent": 98000.12
}
```

### Notes
- Numeric inputs: `area`, `walk`, `age`, `floor`, `rooms`
- Categorical inputs: `ward`, `layout_type`
- Unknown categories (not seen during training) remain zero in one-hot vectors.

### Troubleshooting
- If `artifacts/model.pkl` is missing, run preprocessing and training again.
- If API fails on startup, make sure `data/processed/*` and `artifacts/*` exist.

### Future Improvements
- Stronger input validation
- Compare additional models
- Add tests and CI

---

## 日本語

### 概要
Tokyo Rent Predictor App は、物件特徴量から東京の賃料を予測する機械学習プロジェクトです。  
このリポジトリには、データ前処理・モデル学習・FastAPI による推論 API 提供までの一連の流れが含まれます。

### 主な機能
- **データ前処理**（`src/preprocess.py`）
  - 生データ CSV の読み込み
  - 欠損値処理
  - `type` から `rooms` と `layout_type` を抽出
  - カテゴリ特徴量の One-hot エンコード
  - 数値特徴量の標準化と scaler 情報保存
- **モデル学習**（`src/train.py`）
  - 学習/評価データ分割（`test_size=0.2`, `random_state=42`）
  - `LinearRegression` の学習
  - MSE / RMSE / R² による評価
  - `artifacts/model.pkl` と `artifacts/columns.json` を保存
- **API 提供**（`src/main.py`）
  - `GET /` ヘルスチェック
  - `POST /predict` 予測 API

### ディレクトリ構成
```text
Tokyo-Rent-Predictor-App/
├─ src/
│  ├─ preprocess.py
│  ├─ train.py
│  └─ main.py
├─ data/
│  ├─ raw/
│  │  └─ Data.csv
│  └─ processed/
│     ├─ processed_data.csv
│     └─ scaler_info.csv
└─ artifacts/
   ├─ model.pkl
   └─ columns.json
```

### 必要環境
- Python 3.10+
- 推奨インストール:

```bash
pip install fastapi uvicorn pandas scikit-learn numpy joblib pydantic
```

### クイックスタート
1. 前処理:
```bash
python src/preprocess.py
```
2. 学習:
```bash
python src/train.py
```
3. API 起動:
```bash
uvicorn src.main:app --reload
```
4. ドキュメント:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API
- `GET /`
  - レスポンス:
```json
{"message": "Rent prediction API is running"}
```

- `POST /predict`
  - リクエスト:
```json
{
  "area": 25.5,
  "walk": 8,
  "age": 12,
  "floor": 3,
  "rooms": 1,
  "ward": "Shinjuku",
  "layout_type": "K"
}
```
  - レスポンス:
```json
{
  "predicted_rent": 98000.12
}
```

### 注意点
- 数値入力: `area`, `walk`, `age`, `floor`, `rooms`
- カテゴリ入力: `ward`, `layout_type`
- 学習時に存在しないカテゴリ値は One-hot 上で 0 のままになります。

### トラブルシューティング
- `artifacts/model.pkl` がない場合は前処理と学習を再実行してください。
- API 起動エラー時は `data/processed/*` と `artifacts/*` の存在を確認してください。

### 今後の改善
- 入力バリデーション強化
- 他モデル比較
- テストと CI の追加

---

## 中文

### 项目简介
Tokyo Rent Predictor App 是一个根据房源特征预测东京租金的机器学习项目。  
仓库包含完整流程：数据预处理、模型训练、以及基于 FastAPI 的在线预测服务。

### 主要功能
- **数据预处理**（`src/preprocess.py`）
  - 读取原始 CSV
  - 处理缺失值
  - 将 `type` 拆分为 `rooms` 和 `layout_type`
  - 对类别特征进行 One-hot 编码
  - 对数值特征标准化并保存 scaler 信息
- **模型训练**（`src/train.py`）
  - 划分训练/测试集（`test_size=0.2`, `random_state=42`）
  - 训练 `LinearRegression`
  - 使用 MSE / RMSE / R² 评估
  - 输出 `artifacts/model.pkl` 与 `artifacts/columns.json`
- **API 服务**（`src/main.py`）
  - `GET /` 健康检查
  - `POST /predict` 预测接口

### 目录结构
```text
Tokyo-Rent-Predictor-App/
├─ src/
│  ├─ preprocess.py
│  ├─ train.py
│  └─ main.py
├─ data/
│  ├─ raw/
│  │  └─ Data.csv
│  └─ processed/
│     ├─ processed_data.csv
│     └─ scaler_info.csv
└─ artifacts/
   ├─ model.pkl
   └─ columns.json
```

### 环境要求
- Python 3.10+
- 推荐安装:

```bash
pip install fastapi uvicorn pandas scikit-learn numpy joblib pydantic
```

### 快速开始
1. 数据预处理:
```bash
python src/preprocess.py
```
2. 训练模型:
```bash
python src/train.py
```
3. 启动 API:
```bash
uvicorn src.main:app --reload
```
4. 打开文档:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API
- `GET /`
  - 返回:
```json
{"message": "Rent prediction API is running"}
```

- `POST /predict`
  - 请求体:
```json
{
  "area": 25.5,
  "walk": 8,
  "age": 12,
  "floor": 3,
  "rooms": 1,
  "ward": "Shinjuku",
  "layout_type": "K"
}
```
  - 返回:
```json
{
  "predicted_rent": 98000.12
}
```

### 输入说明
- 数值输入：`area`、`walk`、`age`、`floor`、`rooms`
- 类别输入：`ward`、`layout_type`
- 若出现训练中未见过的类别，其 One-hot 向量会保持为 0。

### 常见问题
- 若缺少 `artifacts/model.pkl`，请重新执行预处理和训练。
- 若 API 启动失败，请确认 `data/processed/*` 与 `artifacts/*` 文件存在。

### 后续改进
- 增强输入校验
- 对比更多模型
- 增加测试与 CI