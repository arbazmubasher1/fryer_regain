import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import altair as alt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Fryer Regain Trend", layout="wide")

st.title("🔥 Fryer Regain Trend Dashboard (Google Sheets Connected)")

# -----------------------------
# Load service account
# -----------------------------
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not credentials_path or not os.path.exists(credentials_path):
    st.error("Missing credentials. Place service_account.json in /credentials and add path to .env")
    st.stop()

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

# -----------------------------
# Your fixed Google Sheet URL
# -----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/14r53FBraAalBclaecplACdvI7vmUctEQDl2Ewv7Pdho/edit#gid=0"

sheet = client.open_by_url(sheet_url).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Cleaning
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Regain Seconds"] = pd.to_numeric(df["Regain Seconds"], errors="coerce")
df = df.sort_values(["Fryer ID", "Product", "Date", "Regain Type"])

# Filters
st.sidebar.header("Filters")
branches = st.sidebar.multiselect("Branch", df["Branch"].unique(), df["Branch"].unique())
fryers = st.sidebar.multiselect("Fryer ID", df["Fryer ID"].unique(), df["Fryer ID"].unique())
products = st.sidebar.multiselect("Product", df["Product"].unique(), df["Product"].unique())

filtered = df[
    (df["Branch"].isin(branches)) &
    (df["Fryer ID"].isin(fryers)) &
    (df["Product"].isin(products))
]

# Trend chart
st.subheader("📊 Overlaid Regain 1 vs Regain 2 Trends (per Fryer)")

for fryer in filtered["Fryer ID"].unique():
    fryer_df = filtered[filtered["Fryer ID"] == fryer]

    chart = alt.Chart(fryer_df).mark_line(point=True).encode(
        x="Date:T",
        y="Regain Seconds:Q",
        color="Regain Type:N",
        tooltip=["Date", "Branch", "Fryer ID", "Product", "Regain Type", "Regain Seconds"]
    ).properties(
        title=f"Fryer: {fryer}",
        width=900,
        height=300
    )

    st.altair_chart(chart, use_container_width=True)

# Data table
st.subheader("📋 Data")
st.dataframe(filtered)
