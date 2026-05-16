class StockMissingError(Exception):
    """The requested ticker symbol does not exist in yfinance.."""

    def __init__(self, ticker: str):
        """Initialize the error with the missing ticker symbol.

        Args:
            ticker: The ticker symbol that could not be resolved.
        """
        self.ticker: str = ticker
        message = f"Stock ticker '{ticker}' not found."
        super().__init__(message)


class DataSourceError(Exception):
    """An external data source returned an error or is unavailable."""

    def __init__(self, source: str, details: str):
        """Initialize the error with the source name and error details.

        Args:
            source: The name of the data source that failed (e.g. "yfinance").
            details: A human-readable description of what went wring.
        """
        self.source: str = source
        self.details: str = details
        message = f"{source} unavailable: {details}"
        super().__init__(message)
