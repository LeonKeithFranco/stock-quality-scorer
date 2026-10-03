# Stock Quality Scorer

A machine learning service that scores S&P 500 stocks on how closely their current fundamentals resemble those of stocks that beat the S&P 500 index over the past 12 months. It is served through a FastAPI REST API with a Streamlit dashboard client.

## Live demo

- **Frontend:** https://stock-quality-scorer-frontend.fly.dev
- **Backend API:** https://stock-quality-scorer-backend.fly.dev/docs

Both are deployed on Fly.io. Both may take a moment to wake from a stopped state.

## What problem this project solves

Retail investors want a quick way to screen stocks for quality without building their own models. This project scrapes current S&P 500 constituents from Wikipedia, pulls fundamentals and price history from Yahoo Finance, trains a calibrated Random Forest classifier on eight financial ratios, and serves scores through a FastAPI backend. The Streamlit frontend lets you enter any ticker or view scores for the entire S&P 500. The target variable is binary: whether or not the stock beat the S&P 500 index over the trailing 12 months. Because the label and the features come from the same point in time, the score describes which fundamentals are associated with recent outperformance; it is not a forecast of future returns (see [Methodology](#methodology)).

## Tech stack

- Python 3.12
- uv
- FastAPI
- Streamlit
- Scikit-learn

## Architecture

The project is split into three workspace members:

- **Machine learning pipeline (`ml/`):** Data collection and model training. Scripts scrape the S&P 500 constituent list from Wikipedia, download fundamentals and 5-year price histories from Yahoo Finance via `yfinance`, generate a training dataset with a binary label for trailing 12-month outperformance, and train a calibrated Random Forest. The final model artifact is serialized with `joblib` and saved to `backend/data/` where the backend reads it at startup.
- **Backend API (`backend/`):** Loads the trained model on startup via a lifespan context manager, fetches live fundamentals from Yahoo Finance for incoming requests, and returns a calibrated score between 0 and 1. Domain exceptions are translated into HTTP status codes via FastAPI exception handlers. Fundamentals and predictions are cached with TTL-based and LFU caches to avoid redundant Yahoo Finance calls.
- **Frontend client (`frontend/`):** A thin client that calls the backend via `httpx`. Supports single-ticker lookup and a full S&P 500 view.

### Data flow:

1. ML pipeline scrapes Wikipedia for the S&P 500 tickers, downloads fundamentals and prices from Yahoo Finance
2. Pipeline generates training dataset, trains and calibrates a Random Forest, serializes it to `backend/data/rf_calibrated.joblib`
3. Going to the Streamlit frontend automatically pulls the S&P 500 scores; the user may also enter a ticker
4. Frontend calls `POST /predict/snp-500` immediately to populate the table; `POST /predict/` when the user requests a score for a specific ticker
5. Backend fetches live fundamentals from Yahoo Finance, runs them through the loaded model, returns the calibrated score
6. Frontend displays the score as a percentage and a binary "Predicted to Beat S&P 500" flag (score above 0.5)

## Running locally

### Prerequisites:

- Python 3.12+
- uv

1. Clone the repo
2. Install dependencies: `uv sync --all-packages`
3. Run the ML pipeline (from `ml/`):
   - `uv run python -m scripts.get_data.grab_data`
   - `uv run python -m scripts.get_data.generate_training_dataset`
   - `uv run python -m scripts.train_model.train_models`
   - `uv run python -m scripts.train_model.calibrate_model`

   `grab_data` downloads fresh data, so the resulting model will differ from one trained on the committed May 2026 snapshot. To train on the committed snapshot instead, skip `grab_data` and run the other three commands.

4. Create `.env` files in both `frontend` and `backend` then copy the contents of the respective `.env.template`
5. Start the backend (from `backend/`): `uv run fastapi dev app/main.py`
6. In a second terminal, start the frontend (from `frontend/`): `uv run streamlit run main.py`
7. Open the frontend client at http://localhost:8501 and wait for the S&P 500 table to populate or enter a ticker symbol

### Podman compose

Running via containers: `podman-compose up --build`

This starts both services, however, the model artifact must already exist in `backend/data/` before building.

## API

### POST /predict/

**Request body:** `{ "ticker" : "AAPL" }`

**Response(200):** `ticker` (normalized to upper case, with `.` replaced by `-` to match Yahoo Finance, e.g. `brk.b` → `BRK-B`), `outperformance_probability` (0.0-1.0, the calibrated model score), and `predicted_class` (1 if `outperformance_probability` > 0.5, else 0)

### POST /predict/snp-500

Returns scores for current S&P 500 constituents. Scrapes the latest constituents list from Wikipedia, fetches live fundamentals for each ticker, and returns an array of predictions. Share-class tickers are converted to Yahoo Finance's format, so Wikipedia's `BRK.B` is returned as `BRK-B`. Tickers that fail (e.g. delisted or rate-limited) are silently excluded.

### Error responses

- 404: ticker not found on Yahoo Finance
- 422: invalid request body (e.g. empty ticker or one longer than 10 characters)
- 503: Yahoo Finance or Wikipedia temporarily unavailable
- 500: unhandled internal error

All error bodies use a `detail` key. For 422 errors its value is FastAPI's list of validation errors; for the others it is a message string.

FastAPI generates interactive docs at `/docs`.

## Methodology

The model is a Random Forest classifier wrapped in `CalibratedClassifierCV` (`method=sigmoid`, 5-fold cross validation), which maps the forest's vote fractions to probability estimates.

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

**Target variable:** Binary. A stock is labeled as `1` if its trailing 12-month return exceeded the S&P 500's trailing 12-month return over the same period, `0` otherwise. The features are fundamentals as of the same date, so the model learns which current ratios are associated with the past year's outperformance. Valuation ratios such as trailing P/E and price-to-book include the current share price, so they partly reflect the same price move the label measures. The score should therefore be read as a description of recent winners, not as a forecast.

**Evaluation:** 5-fold stratified cross-validation scored on ROC AUC. Three model families were compared (Logistic Regression, Random Forest, Gradient Boosting); Random Forest scored highest on the committed May 2026 snapshot (mean AUC about 0.73, versus about 0.70 for Gradient Boosting and 0.66 for Logistic Regression). No random seed is set, so exact scores vary slightly between runs. `calibrate_model.py` prints calibration curves for the raw and calibrated models, but they are computed on the same data the models were trained on, so they show in-sample fit rather than verifying out-of-sample calibration.

## Testing

The test suite is split by scope and workspace member:

- **ML data tests** (`ml/tests/test_data.py`): Validate data integrity at each stage of the pipeline - correct number of tickers, expected column names and types, date range coverage for price data, no duplicate entries, no featureless rows in training data, and that the target label contains only 0s and 1s
- **ML model tests** (`ml/tests/test_model.py`): Load the serialized model artifact and verify that predictions produce valid probability pairs that sum to 1.0, that NaN features are handled gracefully, and that incorrect input shapes raise `ValueError` rather than producing silent garbage
- **Backend unit tests** (`backend/tests/unit/`): Verify that the fundamentals-to-DataFrame conversion preserves the column order the model expects
- **Backend integration tests** (`backend/tests/integration/`): API endpoints via FastAPI's `TestClient`. Yahoo Finance is mocked at the `yf.Ticker` boundary. Tests cover the happy path (valid prediction), missing ticker (404), rate-limit exhaustion (503), invalid request body (422), and the S&P 500 endpoint

### Running tests:

Run each workspace member's tests separately from the repo root, so pytest picks up that member's own configuration:

- ML tests: `uv run pytest ml/tests/`
- Backend tests: `uv run pytest backend/tests/`

The ML model tests and the backend prediction tests need the trained model artifact, so run the ML pipeline (step 3 of Running locally) first.

## Limitations and caveats

This is a portfolio project and the model has real statistical limitations that are worth being upfront about:

- **Survivorship bias:** The training set is today's S&P 500 constituents. Companies that were in the index but got removed (due to poor performance, acquisition, etc.) are excluded. This biases the dataset towards survivors and likely inflates apparent model performance
- **Backward-looking label, no temporal validation:** The model trains on one snapshot of current fundamentals, labeled with the trailing 12-month return over the period those fundamentals already reflect. It has not been tested on whether today's ratios predict the _next_ 12 months, and there's no walk-forward or time-series split to test whether the signal holds across market regimes. A model trained during a bull market may not work in a downturn
- **Current fundamentals only:** Features are point-in-time ratios. The model has no sense of trajectory; it can't distinguish "margins improving from 10% to 20%" from "margins declining from 30% to 20%", both look like 20% to the model
- **Small dataset:** ~500 samples is thin for machine learning. With 8 features and 5-fold CV, overfitting is a genuine concern, and a larger universe of stocks would give more confidence
- **No feature importance analysis:** The model is a black box. There's no SHAP or permutation importance to explain which ratios are driving predictions for a given stock
- **Single data source:** Yahoo Finance is the only source for fundamentals and if it is not available or if `yfinance` breaks, the entire pipeline stops

## Things to include in a v2

- _Historical fundamentals_ for proper time-series training with walk-forward validation; this is the single biggest improvement for model credibility
- _SHAP values_ per prediction so users can see why the model scored a stock the way it did
- _Summary endpoint_ returning feature contributions alongside the prediction
- _Broader universe of stocks_ like the Russell 1000 or all NYSE/NASDAQ stocks to increase training set size and reduce survivorship bias

## Design decisions

- **Binary target over regression:** Classifying whether a stock beat the index rather than by how much, since for most retail investors the decision is either buy or don't
- **12-month return window:** Convention in financial research; short enough to be actionable but long enough to smooth out noise
- **Calibrated probabilities over raw predictions:** A Random Forest's `predict_proba` returns vote fractions, not probabilities. `CalibratedClassifierCV` maps them to probability estimates, with the intent that a 70% score corresponds to roughly 70% of such stocks having outperformed. This hasn't been checked on held-out data yet (see Evaluation)
- **Median imputation:** Some tickers are missing certain fundamentals; Median imputation is simple and avoids data leakage since it's computed per-fold inside the pipeline
- **TTL + LFU caching on the backend:** Fundamentals don't change intraday. A 24-hour TTL on the Yahoo Finance cache and an LFU eviction policy for predictions keeps the backend responsive without stale data

## Lessons learned

### Calibration is not optional for probability-based UIs

Showing users a "72% chance of outperformance" is a strong claim. If that number is just a Random Forest vote, it's misleading. Calibration is the first step toward a number that means something; checking it on held-out data is the second.

### Data pipeline tests pay for themselves immediately

The ML data tests caught silent issues early on:

- Tickers with empty fundamental rows
- Duplicate date-ticker entries in price data

Without those tests, those bugs would have silently surfaced as strange model behaviour.

### Mocking `yfinance` is straightforward once you mock at the right level

Mocking `yf.Ticker` at the class level rather than intercepting HTTP calls gave stable, readable integration tests.

### Survivorship bias is easy to ignore and hard to fix

Acknowledging it honestly is better than pretending it doesn't exist. A v2 with historical constituent lists would address it properly, but that might require a paid data source.
