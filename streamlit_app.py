import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Stocks Correlation", page_icon="📈")
st.title("📈 Stock Correlation")
st.write(
    """
    correlation between stocks from Yahoo Finance
    """
)


