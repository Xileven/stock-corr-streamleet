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

# @st.cache_data
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
# st.sidebar.header("Filter Options")

# ==========================================================================================

# Collapsible filter and sorting options (previously in sidebar)
with st.expander("Filter & Sort Options", expanded=False):
    # Filter by pair
    pair_options = st.multiselect(
        'Select pairs (sorted in ascending order):',
        options=sorted(data['pair'].unique()),  # Sort options in ascending order
        default=data['pair'].unique()
    )
    filtered_data = data[data['pair'].isin(pair_options)]

    # Sorting
    sort_by = st.selectbox('Sort by:', options=filtered_data.columns[1:])
    ascending = st.radio("Sort order", ('Ascending', 'Descending'))

    # Apply sorting
    filtered_data = filtered_data.sort_values(by=sort_by, ascending=(ascending == 'Ascending'))

st.write("### Filtered and Sorted Data")
st.dataframe(filtered_data)

# Line chart
st.write("### Line Chart")
selected_pairs = st.multiselect(
    'Select rows to visualize (sorted in ascending order):',
    options=sorted(filtered_data['pair']),  # Sort in ascending order
    default=sorted(filtered_data['pair'])[:1]  # Default to the first one
)

# Plot data for selected pairs
if selected_pairs:
    chart_data = filtered_data[filtered_data['pair'].isin(selected_pairs)]
    chart_data = chart_data.set_index('pair').T
    
    # Ensure the x-axis (columns of chart_data) follows the original DataFrame order
    chart_data.index = pd.Categorical(chart_data.index, categories=filtered_data.columns[1:], ordered=True)
    chart_data = chart_data.sort_index()

    st.line_chart(chart_data)