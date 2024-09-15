import streamlit as st
import pandas as pd
import math
from pathlib import Path
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Stocks Correlation", 
    page_icon="📈"
)

st.title("📈 Stock Correlation")
st.write("Correlation between stocks from Yahoo Finance")

# Cache the data to speed up subsequent loads
# @st.cache_data
def get_corr_data():
    DATA_FILENAME = Path(__file__).parent / 'data/corr_data.csv'

    # Check if the file exists
    if not DATA_FILENAME.exists():
        st.error(f"File not found: {DATA_FILENAME}")
        return pd.DataFrame()  # Return an empty DataFrame if file is not found

    # Load the data
    raw_corr_df = pd.read_csv(DATA_FILENAME)
    return raw_corr_df

# Load the data
data = get_corr_data()

# If data is empty, stop the app
if data.empty:
    st.stop()

# Collapsible filter and sorting options
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

# Line chart with Plotly
st.write("### Interactive Line Chart")
selected_pairs = st.multiselect(
    'Select rows to visualize (sorted in ascending order):',
    options=sorted(filtered_data['pair']),  # Sort in ascending order
    default=sorted(filtered_data['pair'])[:1]  # Default to the first one
)

# Plot data for selected pairs
if selected_pairs:
    # Filter the data for the selected pairs
    chart_data = filtered_data[filtered_data['pair'].isin(selected_pairs)]
    
    # Transpose the DataFrame so that the x-axis is the time interval
    chart_data = chart_data.set_index('pair').T
    
    # Create an interactive Plotly line chart
    fig = px.line(
        chart_data,
        labels={'value': 'Correlation', 'index': 'Time Interval'},
        title="Correlation over Time",
    )
    
    # Add hover info and markers to make lines clickable
    fig.update_traces(mode='lines+markers', hovertemplate='Time Interval: %{x}<br>Correlation: %{y}<extra></extra>')
    
    # Show the interactive Plotly chart in Streamlit
    st.plotly_chart(fig)