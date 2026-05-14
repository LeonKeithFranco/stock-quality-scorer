from dataclasses import asdict

import streamlit as st
from src.core import api
from src.core.config import get_settings

st.header(get_settings().app_name)

with st.spinner():
    snp_500_predictions = api.predict_snp_500()


st.dataframe([asdict(prediction) for prediction in snp_500_predictions])
