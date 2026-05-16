from dataclasses import asdict

import httpx
import pandas as pd
import streamlit as st
from src.core import api
from src.core.api import PredictionResponse
from src.core.config import get_settings

st.header(get_settings().app_name)


def _create_table(predictions: list[PredictionResponse]) -> None:
    """Render a list of prediction responses as a streamlit table.

    Converts raw predictions into a formatted DataFrame with human-readable column names
    and percentage formatting, then displays it.

    Args:
        predictions: The prediction results to display.
    """
    df_prediction = pd.DataFrame([asdict(prediction) for prediction in predictions])
    df_prediction["outperformance_probability"] = (
        df_prediction["outperformance_probability"] * 100
    ).round(2)
    df_prediction["predicted_class"] = df_prediction["predicted_class"].map(
        lambda v: "Y" if v == 1 else "N"
    )
    df_prediction.columns = [
        "Ticker",
        "Probability of Outperformance",
        "Predicted to Beat S&P 500",
    ]

    column_config = {
        "Probability of Outperformance": st.column_config.NumberColumn(format="%.2f%%")
    }
    st.dataframe(df_prediction, column_config=column_config, hide_index=True)


@st.fragment
def single_predict():
    """Render the single-ticker prediction form and display the results.

    Presents a text input for the ticker symbol and a submit button. On submission, calls
    the backend prediction API and displays the result as a table, or shows an error
    message on failure.
    """
    with st.form("ticker_predict_form"):
        ticker = st.text_input("Enter Ticker", placeholder="AAPL, MSFT, KO, etc.")
        submitted = st.form_submit_button("Predict")

    if submitted:
        if ticker:
            try:
                with st.spinner("Loading..."):
                    prediction = api.predict(ticker)

                _create_table([prediction])
            except httpx.HTTPStatusError as e:
                st.error(f"Unable to get data: {e.response.json()['details']}")
            except Exception as e:
                st.error(f"Unable to get data: {e}")
        else:
            st.warning("Please enter a stock ticker.")


single_predict()

st.divider()

try:
    with st.spinner("Loading full S&P 500 predictions..."):
        snp_500_predictions = api.predict_snp_500()

    _create_table(snp_500_predictions)
except Exception as e:
    st.error(f"Unable to get data: {e}")
