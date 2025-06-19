import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
RAPIDAPI_KEY = "ac1c9412ffmsh11cf86182f0eec4p1e33b7jsn499839f65f6e"
RAPIDAPI_HOST = "yahoo-finance-real-time1.p.rapidapi.com"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSdUAMpLgJeY6LPskB2sKqUTf2utSGfn4qz3CtMrQx0Mz0FXV3T55c6UydF5N2xQo2oVCl9hr7dN88L/pub?output=csv"

# --- Streamlit UI ---
st.set_page_config(page_title="money_double_dash", layout="wide")
st.title("📈 money_double_dash – Live-Watchlist")

# --- Google Sheet laden ---
@st.cache_data(ttl=300)
def load_watchlist():
    return pd.read_csv(SHEET_URL)

watchlist_df = load_watchlist()
tickers = ",".join(watchlist_df["Ticker"].dropna().tolist())

# --- API-Daten abrufen ---
@st.cache_data(ttl=300)
def get_stock_data(tickers):
    url = f"https://{RAPIDAPI_HOST}/market/v2/get-quotes"
    querystring = {"symbols": tickers, "region": "DE"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        result = response.json()
        data = []
        for quote in result.get("quoteResponse", {}).get("result", []):
            data.append({
                "Symbol": quote.get("symbol"),
                "Name": quote.get("shortName"),
                "Preis": quote.get("regularMarketPrice"),
                "Änderung %": quote.get("regularMarketChangePercent")
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return pd.DataFrame()

kurs_df = get_stock_data(tickers)

# --- Anzeige ---
if not kurs_df.empty:
    merged_df = pd.merge(watchlist_df, kurs_df, how="left", left_on="Ticker", right_on="Symbol")
    st.dataframe(merged_df)
else:
    st.warning("Keine Kursdaten verfügbar.")