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
    correlation between stocks from Yahoo Finance
    """
)


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

    def get_sp500_tickers():
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_table = tables[0]
        tickers = sp500_table['Symbol'].tolist()
        
        return tickers

    sp500_tickers = sorted(get_sp500_tickers())

    def get_5_year_history(tickers):
        data = {}
        for ticker in tickers:
            try:
                stock_data = yf.Ticker(ticker)
                hist = stock_data.history(period="5y")
                if not hist.empty:
                    data[ticker] = hist
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        return data

    five_year_history = get_5_year_history(sp500_tickers)

    all_histories_df = pd.DataFrame()
    for ticker, hist in five_year_history.items():
        hist['Ticker'] = ticker  # Add a column for the ticker symbol
        all_histories_df = pd.concat([all_histories_df, hist], axis=0)

    # Reset the index to make 'Date' a column again
    all_histories_df.reset_index(inplace=True)

    stock_info = all_histories_df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    stock_info.columns = [col.lower() for col in stock_info.columns]
    stock_info = stock_info.sort_values(by='date', ascending=False)

    corr_values = ["close", "volume"]

    data = pd.DataFrame()

    for corr_calc_days in [10, 22, 45, 66, 125, 250, 500, 1250]:
    # 1. get prices from BigQuery


        df = {}
        corr = {}
        corr_pair_single = {}
        for corr_value in corr_values:
            # pivot table
            df[corr_value] = stock_info.pivot(index='date', columns='ticker', values=corr_value).sort_index(ascending=True)
            
            # filter time period
            # since it's sorted by date ASC, tail means the last 250 rows
            df[corr_value] = df[corr_value].tail(corr_calc_days)

            # 2. get correlation matrix
            corr[corr_value] = df[corr_value].corr()

            # fill diagonal with nan, 
            # and we want to remove the correlation of a stock with itself
            np.fill_diagonal(corr[corr_value].values, np.nan) 

            # 3. rank
        
            corr[corr_value] = corr[corr_value].reset_index()
            corr_pair_single[corr_value] = pd.melt(corr[corr_value], id_vars='ticker', var_name='other_ticker', value_name=corr_value + '_correlation')


        corr_pair = pd.merge(corr_pair_single['close'], corr_pair_single['volume'], on=['ticker', 'other_ticker'])


        # Assuming 'correlation' is the column you want to sort
        corr_pair = corr_pair.sort_values(by='close_correlation', ascending=False)

        # Drop rows with NaN values in the 'correlation' column
        corr_pair = corr_pair.dropna(subset=['close_correlation'])

        # de-duplicate
        ### For pair `A-B` and `B-A`, we need to remove `B-A` 
        # corr_pair = corr_pair.sort_values(by=['ticker', 'other_ticker'], ascending=[True, True]).drop_duplicates(subset=['close_correlation'])
        corr_pair = corr_pair.sort_values(by=['ticker', 'other_ticker'], ascending=[True, True])
        
        # generate key column by concatenate ticker and other_ticker
        corr_pair['key'] = corr_pair['ticker'] + '_' + corr_pair['other_ticker']
        corr_pair['sorted_key'] = corr_pair.apply(lambda x: '_'.join(sorted(x['key'].split('_'))), axis=1)
        
        # no need to sort here because it's already sorted by ticker and other_ticker
        corr_pair = corr_pair.drop_duplicates(subset=['sorted_key'])

        # Drop the 'key' and 'sorted_key' columns
        corr_pair = corr_pair.drop(columns=['key', 'sorted_key'])

        # Reset index if needed
        corr_pair = corr_pair.reset_index(drop=True)








        # add sector to correlation
        # add infomations to data
        # 1. sectors
        # 2. market cap


        def get_info_for_tickers(tickers, info_name):
            tickers_info = {}
            for ticker in tickers:
                try:
                    tickers_info[ticker] = yf.Ticker(ticker).info[info_name]
                except:
                    tickers_info[ticker] = None
            return tickers_info

        tickers = corr_pair['ticker'].unique()
        get_sector = get_info_for_tickers(tickers, 'sector')
        get_beta = get_info_for_tickers(tickers, 'beta')
        get_shortName = get_info_for_tickers(tickers, 'shortName')
        get_marketCap = get_info_for_tickers(tickers, 'marketCap')
        get_industry = get_info_for_tickers(tickers, 'industry')

        corr_pair['beta_1'] = corr_pair['ticker'].map(get_beta.get)
        corr_pair['beta_2'] = corr_pair['other_ticker'].map(get_beta.get)
        corr_pair['beta_diff'] = corr_pair[['beta_1', 'beta_2']].apply(
                                lambda row: (max(row['beta_1'], row['beta_2']) - min(row['beta_1'], row['beta_2'])) / min(row['beta_1'], row['beta_2']),
                                axis=1
                                )
        # ========================================================================================================================
        # method 2, to compare
        # import numpy as np

        # corr_pair['beta_diff_2'] = np.abs(np.maximum(corr_pair['beta_1'], corr_pair['beta_2']) -
        #                              np.minimum(corr_pair['beta_1'], corr_pair['beta_2'])) / np.minimum(corr_pair['beta_1'], corr_pair['beta_2'])

        # ========================================================================================================================

        corr_pair['marketCap_1'] = corr_pair['ticker'].map(get_marketCap.get)
        corr_pair['marketCap_2'] = corr_pair['other_ticker'].map(get_marketCap.get)

        corr_pair['marketCap_diff'] = corr_pair[['marketCap_1', 'marketCap_2']].apply(
                                lambda row: (max(row['marketCap_1'], row['marketCap_2']) - min(row['marketCap_1'], row['marketCap_2'])) / min(row['marketCap_1'], row['marketCap_2']),
                                axis=1
                                )

        corr_pair['shortName_1'] = corr_pair['ticker'].map(get_shortName.get)
        corr_pair['shortName_2'] = corr_pair['other_ticker'].map(get_shortName.get)


        corr_pair['sector_1'] = corr_pair['ticker'].map(get_sector.get)
        corr_pair['sector_2'] = corr_pair['other_ticker'].map(get_sector.get)
        corr_pair['same_sector'] = corr_pair[['sector_1', 'sector_2']].apply(
                                    lambda row: 1 if row['sector_1']==row['sector_2'] else 0,  
                                    axis=1
                                    )


        corr_pair['industry_1'] = corr_pair['ticker'].map(get_industry.get)
        corr_pair['industry_2'] = corr_pair['other_ticker'].map(get_industry.get)
        corr_pair['same_industry'] = corr_pair[['industry_1', 'industry_2']].apply(
                                    lambda row: 1 if row['industry_1']==row['industry_2'] else 0,  
                                    axis=1
                                    )

        # rename
        corr_pair.rename(columns={'ticker': 'ticker_1', 'other_ticker': 'ticker_2'}, inplace=True)

        # add date and num_of_days used to cal correlation
        import datetime
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        corr_pair['DATA_DUMP_DATE'] = current_date

        corr_pair['corr_calc_days'] = corr_calc_days

        # re-order columns
        corr_pair = corr_pair[['DATA_DUMP_DATE', 'corr_calc_days', 'ticker_1', 'ticker_2', 
                            'close_correlation', 'volume_correlation',
                            'beta_1', 'beta_2', 'beta_diff', 
                            'marketCap_1', 'marketCap_2', 'marketCap_diff', 
                            'shortName_1', 'shortName_2', 
                            'sector_1', 'sector_2', 'same_sector', 
                            'industry_1', 'industry_2', 'same_industry'
                            ]]
        
        if data.empty:
            # st.warning("No data available for the selected tickers.")
            data = corr_pair
        else:
            data = pd.concat([data, corr_pair], axis=0)

    # df = pd.DataFrame(data)    
    df = data

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)    