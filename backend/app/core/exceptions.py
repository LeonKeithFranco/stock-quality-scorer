class StockMissingError(Exception):
    """Error that is throw when yfinance returns a HTTPError for a missing stock."""

    def __init__(self, ticker: str):
        self.ticker: str = ticker
        message = f"Stock ticker '{ticker}' not found."
        super().__init__(message)
