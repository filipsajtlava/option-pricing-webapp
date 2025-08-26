import yfinance as yf
import pandas as pd
import os, requests
import numpy as np
from supabase import create_client
from datetime import datetime, timedelta, timezone
from config import AppSettings, OptionType

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
print("Supabase client initialized.")

def fetch_sp500_tickers(table_name="sp500_tickers"):
    # Might seem unnecessary to overcomplicate the ticker fetching, but the wikipedia url tends 
    # to get changed a lot, so just in case
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    try:
        df = pd.DataFrame()
        df["symbol"] = pd.read_html(response.text)[0]["Symbol"].str.replace(".", "-", regex=False).to_list()
        df["snapshot_date"] = datetime.now(timezone.utc).date().isoformat()
        df = df.to_dict(orient="records")
        supabase_client.table(table_name).delete().neq("symbol", "").execute()
        supabase_client.table(table_name).insert(df).execute()
        print("Current tickers successfully fetched.")
    except:
        print("There is a problem with ticker fetching and upload, defaulting to saved data.")
    response_tickers = supabase_client.table(table_name).select("symbol").execute()
    tickers = pd.DataFrame(response_tickers.data)["symbol"].tolist()
    return tickers

def get_closest_expiry(expirations, days_to_expiry=AppSettings.MODELLED_OPTIONS_EXPIRY_DAYS):
    target_date = pd.to_datetime(datetime.now() + timedelta(days=days_to_expiry))
    closest_index = np.abs((expirations - target_date).total_seconds().to_numpy()).argmin()
    closest = str(expirations[closest_index].date())
    print(f"Closest expiry found: {closest}")
    return closest

def fetch_option_data(yf_ticker, ticker, expiry):
    chain = yf_ticker.option_chain(expiry)
    calls = chain.calls
    puts = chain.puts
    print(f" - {len(calls)} calls, {len(puts)} puts fetched.")

    calls["option_type"] = OptionType.CALL.value
    puts["option_type"] = OptionType.PUT.value
    df = pd.concat([calls, puts], ignore_index=True)

    df["ticker"] = ticker
    df["expiry"] = expiry
    df["snapshot_date"] = datetime.now(timezone.utc).date().isoformat()

    df = df[[
        "contractSymbol", "ticker", "option_type", "strike", 
        "expiry", "bid", "ask", 
        "volume", "impliedVolatility", "snapshot_date"
    ]]

    df["volume"] = df["volume"].fillna(0)
    df["bid"] = df["bid"].fillna(0)
    df["ask"] = df["ask"].fillna(0)

    print(f"Formatted option data for {ticker} with {len(df)} rows.")
    return df

def upload_to_supabase(df, table_name="options_snapshot"):
    supabase_client.table(table_name).delete().neq("ticker", "").execute()
    print(f"Uploading {len(df)} rows to Supabase table '{table_name}'...")
    records = df.to_dict(orient="records")
    supabase_client.table(table_name).insert(records).execute()
    print("Upload to Supabase complete.")

if __name__ == "__main__":
    print("=== OPTIONS SNAPSHOT START ===")
    tickers = fetch_sp500_tickers()
    all_options_df = pd.DataFrame()

    for idx, ticker in enumerate(tickers):
        print(f"\n[{idx+1}/{len(tickers)}] Processing ticker: {ticker}")
        try:
            yf_ticker = yf.Ticker(ticker)
            expirations = pd.to_datetime(yf_ticker.options)
            if len(expirations) == 0:
                print(f"No expirations available for {ticker}. Skipping.")
                continue
            expiry = get_closest_expiry(expirations)
            df = fetch_option_data(yf_ticker, ticker, expiry)
            all_options_df = pd.concat([all_options_df, df], ignore_index=True)
            if ticker == "AAPL" and df["ask"].sum() == 0:
                # hardcoded "AAPL" because of it's reliability, no options will ever cost 0 in total
                # unless the data is corrupted - in that case, exit the entire upload process and wait for another day
                raise SystemExit("Invalid prices detected - exiting the program (probable holiday or weekend)")
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    print(f"\nTotal options rows collected: {len(all_options_df)}")
    if not all_options_df.empty:
        upload_to_supabase(all_options_df)
    else:
        print("No data to upload.")
    print("=== OPTIONS SNAPSHOT COMPLETE ===")