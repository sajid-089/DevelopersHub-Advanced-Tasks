# 📊 DevelopersHub Advanced Tasks (End-to-End ML + Dashboard Project)

This repository contains **3 complete Machine Learning / Data Science tasks** including classification, clustering, time-series forecasting, and a fully interactive Streamlit BI dashboard.

---

## 📁 Project Structure


## Repository Structure
```text
DevelopersHub-Advanced-Tasks/
│
├── data/ # not uploaded to github
│ ├── bank.csv
│ ├── Global_Superstore.csv
│ └── household_power_consumption.txt
│
├── notebooks/
│ ├── task1_term_deposit_XAI.ipynb
│ ├── customer_segmentation.ipynb
│ └── energy_forecasting.ipynb
│
├── outputs/
│ ├── (generated plots: png files from all tasks)
│
├── streamlit_app/
│ └── app.py
││
└── README.md
```


---

# 🚀 Task 1 — Term Deposit Prediction (Classification + Explainability)

## 🎯 Objective
Predict whether a customer will subscribe to a term deposit using machine learning models.

---

## 📌 Workflow

### 1. Data Loading & Preprocessing
- Load `bank.csv` / `bank-full.csv`
- Normalize column names
- Handle missing values
- Convert target variable (`y`) into binary (yes → 1, no → 0)

---

### 2. Exploratory Data Analysis (EDA)
- Target distribution (subscription rate)
- Missing value analysis
- Age distribution
- Job distribution

---

### 3. Feature Engineering
- Numerical + categorical separation
- One-Hot Encoding
- Median/mode imputation
- Train-test split (stratified)

---

### 4. Models
- Logistic Regression (baseline)
- Random Forest (final model)

---

### 5. Evaluation Metrics
- F1 Score
- ROC-AUC
- Confusion Matrix
- ROC Curve

---

### 6. Explainability (SHAP)

We use **SHAP (TreeExplainer)** to interpret Random Forest predictions.

#### Key Outputs:
- 5 individual predictions explained using **waterfall plots**
- Global feature importance (bar plot)
- Beeswarm plot for feature impact distribution

---

### 📌 Business Insights
- Identify top factors influencing subscription
- Understand customer behavior patterns
- Optimize marketing campaigns

---

# 👥 Task 2 — Customer Segmentation (Unsupervised Learning)

## 🎯 Objective
Group customers into meaningful clusters based on behavior and demographics.

---

## 📌 Workflow

### 1. Data Loading
- Dataset: `Mall_Customers.csv`
- Clean and normalize columns

---

### 2. EDA
- Age distribution
- Gender distribution
- Income vs Spending Score relationship

---

### 3. Feature Selection
- Preferred features:
  - Annual Income
  - Spending Score
  - Age (optional)

- Scaling using **StandardScaler**

---

### 4. Clustering Model
- K-Means Clustering
- Elbow Method (Inertia)
- Silhouette Score for optimal K

---

### 5. Visualization
- PCA (2D cluster visualization)
- Optional t-SNE visualization

---

### 6. Cluster Profiling
- Mean & median per cluster
- Boxplots for feature comparison

---

### 7. Business Strategies

Example segmentation logic:

- 💎 High Income + High Spending → Premium customers
- 💰 High Income + Low Spending → Targeted marketing needed
- 🛍️ Low Income + High Spending → Discount-driven campaigns
- 📉 Low Income + Low Spending → Mass promotions

---

# ⚡ Task 3 — Energy Consumption Forecasting (Time Series)

## 🎯 Objective
Forecast household electricity consumption using time series models.

---

## 📌 Dataset
- `household_power_consumption.txt`
- UCI Energy Dataset

---

## 📌 Workflow

### 1. Data Processing
- Parse datetime index
- Resample to hourly frequency
- Handle missing values (interpolation)

---

### 2. Feature Engineering
- Hour
- Day of week
- Weekend flag
- Lag features (1, 2, 3, 24, 48, 72 hours)

---

## 📊 Models

### 📌 Model 1: ARIMA (SARIMAX)
- Seasonal order: 24 (daily seasonality)
- Baseline statistical model

---

### 📌 Model 2: Prophet (Optional)
- Automatic trend + seasonality detection
- Skipped if not installed

```bash
pip install prophet


## Model 3: XGBoost
- Converts time series → supervised learning
- Uses lag + time features

```bash
pip install xgboost

## 📈 Evaluation Metrics
---------------------

*   MAE (Mean Absolute Error)
    
*   RMSE (Root Mean Squared Error)
    

## 📊 Model Comparison
-------------------

*   Compare ARIMA vs Prophet vs XGBoost
    
*   Select best performing model based on error metrics
    

## 📌 Conclusion
-------------

*   Data was cleaned and resampled to hourly format
    
*   Feature engineering improved predictive performance
    
*   Best model selected based on lowest error
    
*   Future improvements:
    
    *   Hyperparameter tuning
        
    *   Rolling window features
        
    *   Longer horizon forecasting
        

## 📊 Streamlit Dashboard — Global Superstore BI App
=================================================

### 🎯 Objective
------------

Build an interactive business intelligence dashboard for sales analysis.