import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt

ZIELWERT = 200000
STARTWERT = 100000
SCHWELLENWERT_DRAWDOWN = -5.0
RAPIDAPI_KEY = "ac1c9412ffmsh11cf86182f0eec4p1e33b7jsn499839f65f6e"
RAPIDAPI_HOST = "yahoo-finance-real-time1.p.rapidapi.com"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-8hdowIqxAFQS39ZRMMQG1UZzFGNr3j7k36IsQUdyE0/export?format=csv"

st.set_page_config(page_title="money_double_dash PRO", layout="wide")
st.title("💹 money_double_dash PRO – Echtzeit-Drawdown & Zieltracking")

@st.cache_data(ttl=300)
def lade_watchlist():
    return pd.read_csv(SHEET_URL)

@st.cache_data(ttl=300)
def get_live_prices(tickers):
    url = f"https://{RAPIDAPI_HOST}/market/v2/get-quotes"
    querystring = {"symbols": ",".join(tickers), "region": "DE"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    response = requests.get(url, headers=headers, params=querystring)
    result = response.json()
    daten = []
    for item in result.get("quoteResponse", {}).get("result", []):
        daten.append({
            "Symbol": item.get("symbol"),
            "Name": item.get("shortName"),
            "Preis": item.get("regularMarketPrice"),
            "Änderung %": item.get("regularMarketChangePercent")
        })
    return pd.DataFrame(daten)

watchlist = lade_watchlist()
tickerliste = watchlist["Ticker"].dropna().tolist()
kurs_df = get_live_prices(tickerliste)
gesamtwert = kurs_df["Preis"].sum() * 1000 / len(kurs_df)

fortschritt = gesamtwert / ZIELWERT
st.metric("📈 Aktueller Depotwert (simuliert)", f"{gesamtwert:,.2f} €", delta=f"{(fortschritt-0.5)*200:.2f} %")
st.progress(min(fortschritt, 1.0))

verlauf = pd.DataFrame({
    "Datum": [datetime.date.today() - datetime.timedelta(days=i*7) for i in range(12)][::-1],
    "Depotwert": [STARTWERT * (1 + i * 0.03) for i in range(11)] + [gesamtwert]
})
verlauf["Depotwert_Vorher"] = verlauf["Depotwert"].shift(1)
verlauf["Drawdown %"] = ((verlauf["Depotwert"] - verlauf["Depotwert_Vorher"]) / verlauf["Depotwert_Vorher"] * 100).fillna(0).round(2)

st.subheader("📉 Depotverlauf mit Drawdown-Erkennung")
fig, ax = plt.subplots()
ax.plot(verlauf["Datum"], verlauf["Depotwert"], marker="o", label="Depotwert")
ax.axhline(ZIELWERT, color="green", linestyle="--", label="Zielwert (200k €)")
ax.set_ylabel("€")
ax.set_xticks(verlauf["Datum"][::2])
ax.set_xticklabels(verlauf["Datum"][::2], rotation=45)
ax.legend()
st.pyplot(fig)

kritische_drawdowns = verlauf[verlauf["Drawdown %"] < SCHWELLENWERT_DRAWDOWN]
if not kritische_drawdowns.empty:
    st.error(f"⚠️ Drawdown erkannt: {kritische_drawdowns.iloc[-1]['Drawdown %']} % am {kritische_drawdowns.iloc[-1]['Datum']}")
    st.dataframe(kritische_drawdowns)
else:
    st.success("✅ Kein kritischer Drawdown in den letzten 12 Wochen.")