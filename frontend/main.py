from dataclasses import asdict

import pandas as pd
import streamlit as st
from src.core import api
from src.core.config import get_settings

st.header(get_settings().app_name)


@st.fragment
def single_predict():
    with st.form("ticker_predict_form"):
        ticker = st.text_input("Enter Ticker", placeholder="AAPL, MSFT, KO, etc.")
        submitted = st.form_submit_button("Predict")

    if submitted:
        if ticker:
            try:
                with st.spinner("Loading..."):
                    prediction = api.predict(ticker)

                df_prediction = pd.DataFrame([asdict(prediction)])
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
                    "Probability of Outperformance": st.column_config.NumberColumn(
                        format="%.2f%%"
                    )
                }
                st.dataframe(
                    df_prediction, column_config=column_config, hide_index=True
                )

            except Exception as e:
                st.error(f"Unable to get data: {e}")
        else:
            st.warning("Please enter a stock ticker.")


single_predict()

st.divider()

try:
    with st.spinner("Loading..."):
        snp_500_predictions = api.predict_snp_500()

    df_snp_500_predictions = pd.DataFrame(
        [asdict(prediction) for prediction in snp_500_predictions]
    )
    df_snp_500_predictions["outperformance_probability"] = (
        df_snp_500_predictions["outperformance_probability"] * 100
    ).round(2)
    df_snp_500_predictions["predicted_class"] = df_snp_500_predictions[
        "predicted_class"
    ].map(lambda v: "Y" if v == 1 else "N")
    df_snp_500_predictions.columns = [
        "Ticker",
        "Probability of Outperformance",
        "Predicted to Beat S&P 500",
    ]

    column_config = {
        "Probability of Outperformance": st.column_config.NumberColumn(format="%.2f%%")
    }
    st.dataframe(df_snp_500_predictions, column_config=column_config, hide_index=True)
except Exception as e:
    st.error(f"Unable to get data: {e}")
