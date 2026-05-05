## Decisions

- SQLite with SQLAlchemy ORM
- db file will live in root of `backend/` folder
- backend will read ml artifacts from `ml/` and load them
- model artifact will be `joblib`
- scrape Wikipedia for S&P 500 tickers and then store results into file
- frontend and backend deployed on `fly.io` together
