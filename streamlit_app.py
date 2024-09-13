import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import os
import yfinance as yf
import pandas as pd
import numpy as np

from yfinance import Ticker 
import yfinance as yf

st.set_page_config(page_title="Stocks Correlation", page_icon="📈")
st.title("📈 Stock Correlation")
st.write(
    """
    Correlation between stocks from Yahoo Finance
    """
)

# Read data from the provided URL
url = "https://storage.cloud.google.com/streamleet-data-bucket/corr_data.parquet"

try:
    st.session_state.df = pd.read_parquet(url)
except Exception as e:
    st.error(f"Error reading Parquet file: {e}")
    st.session_state.df = pd.DataFrame()  # Initialize with an empty DataFrame

if "df" not in st.session_state:
    # Make up some fake issue descriptions.
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]

# Display the DataFrame with sorting and filtering capabilities
st.dataframe(st.session_state.df, use_container_width=True, hide_index=True)

# Add sorting and filtering widgets
sort_column = st.selectbox("Sort by", st.session_state.df.columns)
sort_order = st.selectbox("Sort order", ["Ascending", "Descending"])
filter_column = st.selectbox("Filter by", st.session_state.df.columns)
filter_value = st.text_input(f"Enter {filter_column} value to filter")

# Apply sorting
if sort_order == "Ascending":
    sorted_df = st.session_state.df.sort_values(by=sort_column, ascending=True)
else:
    sorted_df = st.session_state.df.sort_values(by=sort_column, ascending=False)

# Apply filtering
if filter_value:
    filtered_df = sorted_df[sorted_df[filter_column] == filter_value]
else:
    filtered_df = sorted_df

# Display the sorted and filtered DataFrame
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "DATA_DUMP_DATE": st.column_config.DatetimeColumn(
            "Data Dump Date",
            help="Date when the data was dumped",
            format="YYYY-MM-DD",
        ),
        "corr_calc_days": st.column_config.NumberColumn(
            "Correlation Calculation Days",
            help="Number of days used for correlation calculation",
        ),
        "ticker_1": st.column_config.TextColumn(
            "Ticker 1",
            help="First ticker symbol",
        ),
        "ticker_2": st.column_config.TextColumn(
            "Ticker 2",
            help="Second ticker symbol",
        ),
        "close_correlation": st.column_config.NumberColumn(
            "Close Correlation",
            help="Correlation based on closing prices",
        ),
        "volume_correlation": st.column_config.NumberColumn(
            "Volume Correlation",
            help="Correlation based on trading volumes",
        ),
        "beta_1": st.column_config.NumberColumn(
            "Beta 1",
            help="Beta value for Ticker 1",
        ),
        "beta_2": st.column_config.NumberColumn(
            "Beta 2",
            help="Beta value for Ticker 2",
        ),
        "beta_diff": st.column_config.NumberColumn(
            "Beta Difference",
            help="Difference in beta values",
        ),
        "marketCap_1": st.column_config.NumberColumn(
            "Market Cap 1",
            help="Market capitalization for Ticker 1",
        ),
        "marketCap_2": st.column_config.NumberColumn(
            "Market Cap 2",
            help="Market capitalization for Ticker 2",
        ),
        "marketCap_diff": st.column_config.NumberColumn(
            "Market Cap Difference",
            help="Difference in market capitalization",
        ),
        "shortName_1": st.column_config.TextColumn(
            "Short Name 1",
            help="Short name for Ticker 1",
        ),
        "shortName_2": st.column_config.TextColumn(
            "Short Name 2",
            help="Short name for Ticker 2",
        ),
        "sector_1": st.column_config.TextColumn(
            "Sector 1",
            help="Sector for Ticker 1",
        ),
        "sector_2": st.column_config.TextColumn(
            "Sector 2",
            help="Sector for Ticker 2",
        ),
        "same_sector": st.column_config.CheckboxColumn(
            "Same Sector",
            help="Indicates if both tickers are in the same sector",
        ),
        "industry_1": st.column_config.TextColumn(
            "Industry 1",
            help="Industry for Ticker 1",
        ),
        "industry_2": st.column_config.TextColumn(
            "Industry 2",
            help="Industry for Ticker 2",
        ),
        "same_industry": st.column_config.CheckboxColumn(
            "Same Industry",
            help="Indicates if both tickers are in the same industry",
        ),
    },
    disabled=["DATA_DUMP_DATE", "corr_calc_days", "ticker_1", "ticker_2", "close_correlation", "volume_correlation", "beta_1", "beta_2", "beta_diff", "marketCap_1", "marketCap_2", "marketCap_diff", "shortName_1", "shortName_2", "sector_1", "sector_2", "same_sector", "industry_1", "industry_2", "same_industry"],
)