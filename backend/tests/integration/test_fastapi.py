import pytest
from app.core.api import _MAX_ATTEMPTS, get_fundamentals, yf
from app.main import app
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from yfinance.exceptions import YFRateLimitError


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_api_startup(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


class TestAPI:
    @pytest.fixture(autouse=True)
    def clear_fundamentals_cache(self) -> None:
        get_fundamentals.cache.clear()  # ty: ignore[unresolved-attribute]

    def test_predict(self, mocker: MockerFixture, client: TestClient) -> None:
        ticker = "AAPL"

        mock_ticker_instance = mocker.MagicMock()
        mock_ticker_instance.info = {
            "symbol": ticker,
            "trailingPE": 36.29515,
            "priceToBook": 41.244488,
            "returnOnEquity": 1.4147099,
            "debtToEquity": 79.548,
            "revenueGrowth": 0.166,
            "grossMargins": 0.47862,
            "operatingMargins": 0.32275,
            "profitMargins": 0.27152002,
        }

        mock_ticker_class = mocker.patch.object(
            yf, "Ticker", return_value=mock_ticker_instance
        )

        response = client.post("/predict", json={"ticker": ticker})

        mock_ticker_class.assert_called_once_with(ticker)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["ticker"] == ticker
        assert 1.0 >= data["outperformance_probability"] >= 0.0
        assert data["predicted_class"] == (
            1 if data["outperformance_probability"] > 0.5 else 0
        )

    def test_predict_stock_missing_error(
        self, mocker: MockerFixture, client: TestClient
    ) -> None:
        ticker = "AAPL"

        mock_ticker_instance = mocker.MagicMock()
        mock_ticker_instance.info = {}

        mock_ticker_class = mocker.patch.object(
            yf, "Ticker", return_value=mock_ticker_instance
        )

        response = client.post("/predict", json={"ticker": ticker})

        mock_ticker_class.assert_called_once_with(ticker)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "details": f"Stock with ticker symbol '{ticker}' does not exist."
        }

    def test_predict_get_fundamentals_retry(
        self, mocker: MockerFixture, client: TestClient
    ) -> None:
        mocker.patch("app.core.api.time")

        ticker = "AAPL"

        mock_ticker_class = mocker.patch.object(
            yf, "Ticker", side_effect=YFRateLimitError
        )

        response = client.post("/predict", json={"ticker": ticker})

        assert mock_ticker_class.call_count == _MAX_ATTEMPTS

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "details": f"Stock with ticker symbol '{ticker}' does not exist."
        }
