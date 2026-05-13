class StockMissingError(Exception):
    """Error that is throw when yfinance returns a HTTPError for a missing stock."""

    def __init__(self, ticker: str):
        self.ticker: str = ticker
        message = f"Stock ticker '{ticker}' not found."
        super().__init__(message)


class DataSourceError(Exception):
    """Error that is thrown when an api call throws an error"""

    def __init__(self, source: str, details: str):
        self.source: str = source
        self.details: str = details
        message = f"{source} unavailable: {details}"
        super().__init__(message)
