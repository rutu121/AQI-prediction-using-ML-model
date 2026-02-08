# AQI-prediction-using-ML-model

AQI prediction using Machine Learning for my college project.

## Goal
Design a model that fetches real-time air quality data from a government website and predicts AQI for the next 7 days.

## Proposed system design
### 1) Data sources (government)
- **Primary source:** National/State air quality portals (e.g., CPCB/NAQI in India) that publish real-time AQI and pollutant concentrations.
- **Fallback source:** State-level environmental agency dashboards (if the primary source is unavailable).
- **Data types:** AQI, PM2.5, PM10, NO2, SO2, CO, O3, meteorological signals (temp, humidity, wind, rainfall).

### 2) Data ingestion layer
- **Fetcher:** A scheduled job (cron/Airflow/Prefect) calling government APIs or HTML scrapers (only if no API exists).
- **Normalization:** Standardize units, timestamps (UTC), station IDs, and handle missing values.
- **Storage:**
  - Raw data lake (CSV/Parquet on disk or object storage).
  - Cleaned, analytics-ready table (SQLite/Postgres).

### 3) Feature engineering
- **Temporal features:** Day-of-week, month, holiday indicators.
- **Lag features:** 1–7 day lags for AQI and pollutants.
- **Rolling aggregates:** 3/7/14-day rolling mean and standard deviation.
- **Meteorology joins:** Combine weather forecasts to improve 7-day AQI prediction.

### 4) Modeling approach
- **Baseline:** Prophet or SARIMAX for quick 7-day forecasts.
- **Improved model:** Gradient boosting (XGBoost/LightGBM) on engineered features.
- **Deep learning option:** LSTM/Temporal Convolutional Network for multivariate sequences.
- **Target:** Daily AQI for each city/station.

### 5) Training & evaluation
- **Split:** Time-based split (train on past, validate on recent months).
- **Metrics:** MAE, RMSE, and MAPE per station and overall.
- **Retraining:** Weekly/monthly depending on data drift.

### 6) Prediction pipeline
1. Fetch last 30–90 days of real-time data.
2. Merge with weather forecast for next 7 days.
3. Generate features for each future day.
4. Predict AQI for days 1–7.
5. Store and expose results via API or dashboard.

### 7) Deployment and monitoring
- **API:** FastAPI/Flask endpoint `/forecast?city=...` returning 7-day AQI predictions.
- **Dashboard:** Simple web UI or notebook visualization.
- **Monitoring:** Track data freshness, model drift, prediction errors.

## Minimal implementation plan
1. Build a data fetcher that collects daily AQI + pollutants from a government API.
2. Store and clean data in a local database.
3. Train a baseline model (Prophet or XGBoost).
4. Build a prediction script that outputs the next 7-day AQI.
5. Add a lightweight API endpoint to serve predictions.

## Quickstart (baseline model)
Run the baseline 7-day forecast using the sample data:

```bash
python src/aqi_forecast.py --data data/sample_aqi.csv
```

This produces a CSV-style output with the next 7 days of AQI forecasts.
