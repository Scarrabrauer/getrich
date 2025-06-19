import streamlit as st
import pandas as pd

st.set_page_config(page_title="📄 GitHub CSV Test", layout="wide")
st.title("🔍 CSV-Test: GitHub ➜ Streamlit")

CSV_PATH = "https://raw.githubusercontent.com/Scarrabrauer/getrich/main/watchlist.csv"

st.info(f"📥 CSV wird geladen von: {CSV_PATH}")

try:
    df = pd.read_csv(CSV_PATH)
    st.success("✅ CSV erfolgreich geladen!")
    st.dataframe(df)
except Exception as e:
    st.error("❌ Fehler beim Laden der CSV-Datei:")
    st.exception(e)