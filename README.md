## Decisions

- SQLite with SQLAlchemy ORM
- db file will live in root of `backend/` folder
- backend will read ml artifacts from `ml/` and load them
- model artifact will be `joblib`
- scrape Wikipedia for S&P 500 tickers and then store results into file
- frontend and backend deployed on `fly.io` together
- target label is a binary feature instead of magnitude; it aims to answer "will it outperform?" rather than "how much does it outperform/underperform?"
- rate of return time period chosen due to convention of 12 months
