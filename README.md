# Stock Quality Scorer

A machine learning service that predicts which stocks will outperform the S&P 500 index over a 12-month horizon. It is served through a FastAPI REST API with a Streamlit dashboard client.

## Live demo

- **Frontend:** https://stock-quality-scorer-frontend.fly.dev
- **Backend API:** https://stock-quality-scorer-backend.fly.dev/docs

Both are deployed on Fly.io. Both may take a moment to wake from a stopped state.

## What problem this project solves

Retail investors want a quick way to screen stocks for quality without building their own models. This project scrapes current S&P 500 constituents from Wikipedia, pulls fundamentals and price history from Yahoo Finance, trains a calibrated Random Forest classifier on eight financial ratios, and serves predictions through a FastAPI backend. The Streamlit frontend lets you enter any ticker or view predictions for the entire S&P 500. The target variable is binary, whether or not the stock has beat the S&P 500 index, to enable a quick decision.

## Architecture

The project is split into three workspace members:

- **Machine learning pipeline (`ml/`):** Data collection and model training. Scripts scrape the S&P 500 constituent list from Wikipedia, download fundamentals and 5-year price histories from Yahoo Finance via `yfinance`, generate a training dataset with a binary outperformance label, and train a calibrated Random Forest. The final model artifact is serialized with `joblib` and saved to `backend/data/` where the backend reads it at startup.
- **Backend API (`backend/`):** Loads the trained model on startup via a lifespan context manager, fetches live fundamentals from Yahoo Finance for incoming requests, and returns calibrated outperformance probabilities. Domain exceptions are translated into HTTP status codes via FastAPI exception handlers. Fundamentals and predictions are cached with TTL-based and LFU caches to avoid redundant Yahoo Finance calls.
- **Frontend client (`frontend/`):** A thin client that calls the backend via `httpx`. Supports single-ticker lookup and a full S&P 500 view.

### Data flow:

1. ML pipeline scrapes Wikipedia for the S&P 500 tickers, downloads fundamentals and prices from Yahoo Finance
2. Pipeline generates training dataset, trains and calibrates a Random Forest, serializes it to `backend/data/rf_calibrated.joblib`
3. Going to the Streamlit frontend automatically pulls the S&P 500 predictions; the user may also enter a ticker
4. Frontend calls `POST /predict/snp-500` immediately to populate the table; `POST /predict` when user requests prediction for a specific ticker
5. Backend fetches live fundamentals from Yahoo Finance, runs them through the loaded model, returns the calibrated probability
6. Frontend displays the prediction as a probability and a binary "Predicted to Beat S&P 500" flag

## Running locally

### Prerequisites:
- Python 3.12+
- uv

1. Clone the repo
2. Install dependencies: `uv sync --all-packages`
3. Run the ML pipeline:
  - `cd ml`
  - `uv run python -m scripts.get_data.grab_data`
  - `uv run python -m scripts.get_data.generate_training_dataset`
  - `uv run python -m scripts.train_model.train_models`
  - `uv run python -m scripts.train_model.calibrate_model`
4. Create `.env` files in both `frontend` and `backend` then copy the contents of the respective `.env.template`
5. Start the backend: `cd backend && uv run fastapi dev app/main.py`
6. Start the frontend: `cd frontend && uv run streamlit run main.py`
7. Open the frontend client at http://localhost:8501 and wait for the S&P 500 table to populate or enter a ticker symbol

### Podman compose

Running via containers: `podman-compose up --build`

This starts both services, however, the model artifact must already exist in `backend/data/` before building.

## API

### POST /predict/

**Request body:** `{ "ticker" : "AAPL" }`

**Response(200):** `ticker`, `outperformance_probability` (0.0-1.0), and `predicted_class` (1 if `outperformance_probability` > 0.5, else 0)

### POST /predict/snp-500

Returns predictions for all current S&P 500 constituents. Scrapes the latest constituents list from Wikipedia, fetches live fundamentals for each ticker, and returns an array of predictions. Tickers that fail (delisted, rate-limited) are silently excluded.

### Error responses

- 404: ticker not found on Yahoo Finance
- 503: Yahoo Finance or Wikipedia temporarily unavailable
- 500: unhandled internal error

FastAPI generates interactive docs at `/docs`.

## Methodology

The model is a Random Forest classifier and calibrated (`CalibratedClassifierCV` with `method=sigmoid` and 5-fold cross validation) so that `predict_proba` outputs are true calibrated probabilities rather than vote fractions.

### Features (8 financial ratios)

- Trailing P/E ratio (`trailingPE`)
- Price-to-book ratio (`priceToBook`)
- Return on equity (`returnOnEquity`)
- Debt-to-equity ratio (`debtToEquity`)
- Revenue growth (`revenueGrowth`)
- Gross margin (`grossMargins`)
- Operating margin (`operatingMargins`)
- Profit margin (`profitMargins`)

These were chosen because they capture valuation, profitability, leverage, and growth; these are the four dimensions a fundamental analyst typically screens for. Missing values are imputed with the median and features are standardized. The pipeline is wrapped in scikit-learn `Pipeline` so preprocessing and prediction are a single step.

**Target variables:** Binary. A stock is labeled as `1` if its trailing 12-month return exceeded the S&P 500's trailing 12-month return over the same period, `0` otherwise.

**Evaluation:** 5-fold stratified cross-validation scored on ROC AUC. Three model families were compared (Logistic Regression, Random Forest, Gradient Boosting); Random Forest was selected based on AUC performance. Calibration curves (reliability diagrams) were used to verify that the sigmoid calibration improved probability alignment across bins.

## Testing

The test suite is split by scope and workspace member:

- **ML data tests** (`ml/tests/test_data.py`): Validate data integrity at each stage of the pipeline - correct number of tickers, expected column names and types, date range coverage for price data, no duplicate entries, no featureless rows in training data, and that the target label contains only 0s and 1
- **ML model tests** (`ml/tests/test_model.py`): Load the serialized model artifact and verify that predictions produce valid probability pairs that sum to 1.0. that NaN features are handled gracefully, and that incorrect input shapes raise `ValueError` rather than producing silent garbage
- **Backend unit tests** (`backend/tests/unit/`): Verify that the fundamentals-to-Dataframe conversion preserves the column order the model expects
- **Backend integration tests** (`backend/tests/integration/`): API endpoints via FastAPI's `TestClient`. Yahoo finance is mocked at the `yf.Ticker` boundary. Tests verify the happy path (valid prediction), missing ticker (404), rate-limit exhaustion (503), and invalid request body (422)

### Running tests:

- All tests: `uv run pytest`
- ML tests only: `uv run pytest ml/tests/`
- Backend tests only: `uv run pytest backend/tests/`

## Limitations and caveats

This is a portfolio project and the model has real statistical limitations that are worth being upfront about:

- **Survivorship bias:** The training set is today's S&P 500 constituents. Companies that were in the index but got removed (due to poor performance, acquisition, etc.) are excluded. This biases the dataset towards survivors and likely inflates apparent model performance
- **Single cross-section, no temporal validation:** The model trains on one snapshot of fundamentals and one window of returns. There's no walk-forward or time-series split to test whether the signal generalized across market regimes. A model trained during a bull market may not work in a downturn
- **Current fundamentals only:** Features are point-in-time ratios. The model has no sense of trajectory; it can't distinguish "margins improving from 10% to 20%" from "margins declining from 30% to 20%", both looks like 20% to the model
- **Small dataset:** ~500 samples is thin for machine learning. With 8 features and 5-fold CV, overfitting is a genuine concern. The calibration step helps, but a larger universe of stocks would give more confidence
- **No features importance analysis:** The model is a black box. There's no SHAP or permutation importance to explain which ratios are driving predictions for a given stock
- **Single data source:** Yahoo Finance is the only source for fundamentals and so if it is not available or if `yfinance` breaks, the entire pipeline stops

## Things to include in a v2

- *Historical fundamentals* for proper time-series training with walk-forward validation; this is the single biggest improvement for model credibility
- *SHAP values* per prediction so users can see why the model scored a stock the way it did
- *Summary endpoint* returning feature contributions alongside the prediction
- *Broader universe of stocks* like the Russell 1000 or all NYSE/NASDAQ stocks to increase training set size and reduce survivorship bias

## Design decisions

- **Binary target over regression:** Predicting if it will outperform rather than predicting by how much since for most retail investors the decision is either buy or don't
- **12-month return window:** Convention in financial research; short enough to be actionable but long enough to smooth out noise
- **Calibrated probabilities over raw predictions:** A Random Forest's `predict_proba` returns votes, not true probabilities. Using `CalibratedClassifierCV` corrects this so that a 70% prediction actually means outperformance ~70% of the time
- **Median imputation:** Some tickers are missing certain fundamentals; Median imputation is simple and avoids data leakage since it's computed per-fold inside the pipeline
- **TTL + LFU caching on the backend:** Fundamentals don't change intraday. A 24-hour TTL on the Yahoo Finance cache and an LFU eviction policy for predictions keeps the backend responsive without stale data

## Lessons learned

### Calibration is not optional for probability-based UIs

Showing users a "72% change of outperformance" is a strong claim. If that number is just a Random Forest vote, it's misleading. The calibration step was extra work, but it's the difference between a number that means something and a number that doesn't.

### Data pipeline tests pay for themselves immediately

The ML data tests caught silent issues early on:

- Tickers with empty fundamental rows
- Duplicate date-ticker entries in price data

Without these those tests, those bugs would have silently surfaced as strange model behaviour.

### Mocking `yfinance` is straightforward once you mock at the right level

Mocking `yf.Ticker` at the class level rather than intercepting HTTP calls gave stable, readable integration tests.

### Survivorship bias is easy to ignore and hard to fix

Acknowledging it honestly is better than pretending it doesn't exist. A v2 with historical constituent lists would address it properly, but that might require a paid data source.
