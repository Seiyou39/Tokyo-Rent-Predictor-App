# Tokyo Rent Predictor App
<https://tokyo-rent-predictor-app.onrender.com/>

---

## English

### Overview
Tokyo Rent Predictor App is a machine-learning project for predicting apartment rent in Tokyo from property features.  
The repository now contains a full workflow with modular engineering structure: **data crawling, preprocessing, feature encoding/scaling, model training/inference, API service, and frontend UI**.

### Current Architecture
- **Data layer**
  - `src/data/summo_crawler.py`: crawl/listing data collection
  - `src/data/preprocess.py`: cleaning and preprocessing pipeline
- **Feature layer**
  - `src/features/onehot_encoder.py`: categorical one-hot encoding
  - `src/features/scaler.py`: numeric scaling utilities
- **Model layer**
  - `src/model/train.py`: training and evaluation
  - `src/model/predict.py`: model inference logic
- **API layer**
  - `src/api/main.py`: FastAPI app and prediction endpoint(s)
- **Frontend**
  - `frontend/templates/index.html`
  - `frontend/static/script.js`, `style.css`

### Key Updates Implemented
1. **Data collection / processing** pipeline updated.
2. **Data leakage fixed** in standardization:
   - split train/test first
   - compute mean/std on `X_train` only
   - apply to both `X_train` and `X_test`
3. **Collinearity issue (`area` vs `rooms`)** handled in current version.
4. Data scope refined to **1R–2LDK** due to sparse samples in other types.
5. Planning additional feature interactions (e.g., `area_x_Minato`).
6. Frontend/API validation constraints strengthened:
   - `floor` must be integer
   - `floor <= 50`
   - `walk <= 30` minutes

### Leakage-Safe Modeling Pipeline
1. Raw/Clean data  
2. `train_test_split`  
3. Compute mean/std from `X_train` only  
4. Standardize:
   - `X_train` with train stats
   - `X_test` with same train stats  
5. Train model  
6. Evaluate on test set  

### Project Structure
```text
tokyo_rent_predictor/
├─ src/
│  ├─ api/
│  │  └─ main.py
│  ├─ data/
│  │  ├─ preprocess.py
│  │  └─ summo_crawler.py
│  ├─ features/
│  │  ├─ onehot_encoder.py
│  │  └─ scaler.py
│  └─ model/
│     ├─ predict.py
│     └─ train.py
├─ frontend/
│  ├─ templates/
│  │  └─ index.html
│  └─ static/
│     ├─ script.js
│     ├─ style.css
│     └─ images/
├─ data/
│  ├─ raw/
│  │  ├─ 2026-3-28_raw/
│  │  └─ 2026-4-02_raw/
│  └─ processed/
│     ├─ 2026-03-28_data/
│     └─ 2026-04-02_data/
└─ models/
   ├─ columns.json
   └─ scaler_info.csv
```

### Data Versioning
- **Raw data** is saved by date folders (`data/raw/YYYY-M-D_raw/`).
- **Processed data** is also versioned by date (`data/processed/YYYY-MM-DD_data/`).
- Current artifact folder includes preprocessing metadata in `models/`.

### Requirements
- Python 3.10+
- Install dependencies from your project requirements file:
```bash
pip install -r requirements.txt
```

### Quick Start
1. (Optional) Collect data:
```bash
python src/data/summo_crawler.py
```
2. Preprocess data:
```bash
python src/data/preprocess.py
```
3. Train model:
```bash
python src/model/train.py
```
4. Run API:
```bash
uvicorn src.api.main:app --reload
```
5. Open app/docs:
- App/API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Typical Prediction Inputs
- Numeric: `area`, `walk`, `age`, `floor`, `rooms`
- Categorical: `ward`, `layout_type`
- Unknown categories are handled via one-hot default-zero behavior.

### Notes
- Current training focus is **1R to 2LDK** for sample consistency.
- Validation constraints are enforced to reduce frontend test bugs.
- If model artifacts are missing, rerun preprocess + train pipeline.

### Future Work
- Add interaction features (`area × ward`, etc.)
- Add and compare stronger models
- Add unit/integration tests and CI
- Expand data coverage with balanced sampling

---

## 日本語

### 概要
Tokyo Rent Predictor App は、物件特徴量から東京の賃料を予測する機械学習プロジェクトです。  
現在は、**データ収集・前処理・特徴量変換・学習/推論・FastAPI・フロントエンド**まで、モジュール分割した構成になっています。

### 現在の構成
- **データ層**
  - `src/data/summo_crawler.py`：物件データ収集
  - `src/data/preprocess.py`：前処理
- **特徴量層**
  - `src/features/onehot_encoder.py`：カテゴリの One-hot
  - `src/features/scaler.py`：数値スケーリング
- **モデル層**
  - `src/model/train.py`：学習・評価
  - `src/model/predict.py`：推論
- **API 層**
  - `src/api/main.py`：FastAPI エンドポイント
- **フロントエンド**
  - `frontend/templates/index.html`
  - `frontend/static/script.js`, `style.css`

### 実施済みアップデート
1. データ収集/処理フローを更新。  
2. 標準化時の**データリークを修正**。  
3. `area` と `rooms` の共線性問題に対応。  
4. サンプル不足のため、対象を **1R〜2LDK** に集中。  
5. 交互作用特徴量（例：`area_x_Minato`）を追加予定。  
6. フロント/API バリデーションを強化（`floor` 整数、`floor<=50`, `walk<=30`）。

### リーク対策済み学習手順
1. 原始/整形データ  
2. `train_test_split`  
3. `X_train` のみで mean/std 算出  
4. 同じ統計量で `X_train`/`X_test` を標準化  
5. 学習  
6. テスト評価  

### ディレクトリ構成
```text
tokyo_rent_predictor/
├─ src/
│  ├─ api/
│  │  └─ main.py
│  ├─ data/
│  │  ├─ preprocess.py
│  │  └─ summo_crawler.py
│  ├─ features/
│  │  ├─ onehot_encoder.py
│  │  └─ scaler.py
│  └─ model/
│     ├─ predict.py
│     └─ train.py
├─ frontend/
│  ├─ templates/
│  │  └─ index.html
│  └─ static/
│     ├─ script.js
│     ├─ style.css
│     └─ images/
├─ data/
│  ├─ raw/
│  │  ├─ 2026-3-28_raw/
│  │  └─ 2026-4-02_raw/
│  └─ processed/
│     ├─ 2026-03-28_data/
│     └─ 2026-04-02_data/
└─ models/
   ├─ columns.json
   └─ scaler_info.csv
```

### 実行方法
```bash
python src/data/preprocess.py
python src/model/train.py
uvicorn src.api.main:app --reload
```

### 今後の改善
- 交互作用特徴量の拡張
- モデル比較
- テスト/CI 強化
- データ拡張と分布バランス改善

---

## 中文

### 项目简介
Tokyo Rent Predictor App 是一个基于房源特征预测东京租金的机器学习项目。  
目前工程已模块化为：**数据采集、预处理、特征编码/缩放、模型训练与推理、FastAPI 接口、前端页面**。

### 当前工程模块
- **数据层**
  - `src/data/summo_crawler.py`：采集数据
  - `src/data/preprocess.py`：数据清洗与预处理
- **特征层**
  - `src/features/onehot_encoder.py`：类别 One-hot 编码
  - `src/features/scaler.py`：数值标准化
- **模型层**
  - `src/model/train.py`：训练与评估
  - `src/model/predict.py`：推理
- **API 层**
  - `src/api/main.py`：FastAPI 服务
- **前端层**
  - `frontend/templates/index.html`
  - `frontend/static/script.js`, `style.css`

### 已完成更新
1. 完成新一版数据采集/处理流程。  
2. 修复标准化阶段的数据泄露问题。  
3. 处理 `area` 与 `rooms` 共线性。  
4. 数据范围聚焦在 **1R–2LDK**。  
5. 计划增加交互特征（如 `area_x_Minato`）。  
6. 前端/接口输入限制增强（楼层整数、楼层不超过 50、步行不超过 30 分钟）。

### 防泄露训练流程
1. 原始数据  
2. `train_test_split`  
3. 仅用 `X_train` 计算 mean/std  
4. 用同一组统计量标准化 `X_train` 与 `X_test`  
5. 训练模型  
6. 测试评估  

### 目录结构
```text
tokyo_rent_predictor/
├─ src/
│  ├─ api/
│  │  └─ main.py
│  ├─ data/
│  │  ├─ preprocess.py
│  │  └─ summo_crawler.py
│  ├─ features/
│  │  ├─ onehot_encoder.py
│  │  └─ scaler.py
│  └─ model/
│     ├─ predict.py
│     └─ train.py
├─ frontend/
│  ├─ templates/
│  │  └─ index.html
│  └─ static/
│     ├─ script.js
│     ├─ style.css
│     └─ images/
├─ data/
│  ├─ raw/
│  │  ├─ 2026-3-28_raw/
│  │  └─ 2026-4-02_raw/
│  └─ processed/
│     ├─ 2026-03-28_data/
│     └─ 2026-04-02_data/
└─ models/
   ├─ columns.json
   └─ scaler_info.csv
```

### 快速开始
```bash
python src/data/preprocess.py
python src/model/train.py
uvicorn src.api.main:app --reload
```

### 后续计划
- 增加更多交互特征
- 比较更多模型
- 增强测试与 CI
- 扩展并平衡数据覆盖范围