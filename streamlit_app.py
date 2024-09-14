import streamlit as st
import pandas as pd
import math
from pathlib import Path


st.set_page_config(
    page_title="Stocks Correlation", 
    page_icon="📈"
)

st.title("📈 Stock Correlation")
st.write(
    """
    Correlation between stocks from Yahoo Finance
    """
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_corr_data():

    DATA_FILENAME = Path(__file__).parent/'data/corr_data.csv'
    raw_corr_df = pd.read_csv(DATA_FILENAME)

    return raw_corr_df

# corr_df = get_corr_data()





# Load the data
# data_path = 'corr_data.csv'  # Update this if needed
# data = pd.read_csv(data_path)
data = get_corr_data()
# Sidebar options for sorting, filtering, and selection
st.sidebar.header("Filter Options")

# Filter by pair
pair_options = st.sidebar.multiselect('Select pairs:', options=data['pair'].unique(), default=data['pair'].unique())
filtered_data = data[data['pair'].isin(pair_options)]

# Sorting
sort_by = st.sidebar.selectbox('Sort by:', options=filtered_data.columns[1:])
ascending = st.sidebar.radio("Sort order", ('Ascending', 'Descending'))

# Apply sorting
filtered_data = filtered_data.sort_values(by=sort_by, ascending=(ascending == 'Ascending'))

# Main section
st.title('Correlation Data Viewer')

st.write("### Filtered and Sorted Data")
st.dataframe(filtered_data)

# Line chart
st.write("### Line Chart")
selected_pairs = st.multiselect('Select rows to visualize:', options=filtered_data['pair'], default=filtered_data['pair'][0])

# Plot data for selected pairs
if selected_pairs:
    chart_data = filtered_data[filtered_data['pair'].isin(selected_pairs)]
    chart_data = chart_data.set_index('pair').T
    st.line_chart(chart_data)