import pandas as pd
import yfinance as yf
import streamlit as st
import numpy as np
from datetime import datetime
from config import OptionType, TRADING_YEAR_DAYS

@st.cache_data
def get_stock_data(selected_ticker, selected_interval, config):
    df = yf.download(selected_ticker,
                     interval=selected_interval,
                     period=config.MAX_PERIODS[selected_interval]
                     )
    df = df.xs(selected_ticker, axis=1, level=1)
    return df

@st.cache_data
def get_tickers(_supabase_client):
    tickers = _supabase_client.rpc("get_unique_tickers").execute()
    return tickers.data

def get_data_from_supabase(supabase_client, selected_ticker):
    options = supabase_client.rpc("get_options_by_ticker", {"ticker_text": selected_ticker}).execute()
    options_data = pd.DataFrame(options.data)
    return options_data

def get_specific_data(df, option_type):
    if option_type in (OptionType.CALL.value, OptionType.PUT.value):
        df = df[df["option_type"] == option_type]
    else:
        raise ValueError("Please select one of the possible option types.")
    
    closest_expiry = df.loc[df.index[0], "expiry"]
    df = df.loc[:, ["contractsymbol", "strike", "bid", "ask", "volume", "impliedvolatility"]]
    df.columns = ["Contract symbol", "Strike price (K)", "Bid", "Ask", "Volume", "Implied volatility (IV)"]
    df = df.set_index("Contract symbol")

    closest_expiry = datetime.strptime(closest_expiry, "%Y-%m-%d")
    closest_expiry = datetime.strftime(closest_expiry, "%d.%m.%Y")
    return df, closest_expiry

def data_older_than_yesterday(df):
    data_input_date = df["snapshot_date"][0]
    data_input_date = datetime.strptime(data_input_date, "%Y-%m-%d")
    data_input_date_regionalized = datetime.strftime(data_input_date, "%d.%m.%Y")
    
    if (datetime.now() - data_input_date).days > 0:
        return data_input_date_regionalized
    return None

@st.cache_data
def calculate_historical_volatility(selected_ticker, config):
    df = yf.download(selected_ticker,
                     interval=config.HV_INTERVAL,
                     period=config.HV_PERIOD
                     )
    df = df.xs(selected_ticker, axis=1, level=1)
    historical_volatility = np.log(df["Close"] / df["Close"].shift(1)).std() * np.sqrt(TRADING_YEAR_DAYS)

    return historical_volatility

@st.cache_data(ttl=3600)
def get_risk_free_rate():
    try:
        shy = yf.Ticker("SHY")
        risk_free_rate = shy.info["dividendYield"] / 100 
        if risk_free_rate is None or risk_free_rate == 0:
            return 0.04  # Fallback to 4 %
        return risk_free_rate
    except Exception as e:
        return 0.04
