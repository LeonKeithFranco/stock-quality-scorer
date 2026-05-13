import pytest
from app.core.api import yf
from app.main import app
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_api_startup(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


class TestAPI:
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

        response = client.post("/predict", json={"ticker": "AAPL"})

        mock_ticker_class.assert_called_once_with(ticker)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["ticker"] == ticker
        assert data["outperformance_probability"] > 0.5
        assert data["predicted_class"] == 1
