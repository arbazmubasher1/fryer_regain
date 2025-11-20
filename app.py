import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import altair as alt

st.set_page_config(page_title="Fryer Regain Trend", layout="wide")

st.title("🔥 Fryer Regain Trend Dashboard (Google Sheets Connected)")

# -----------------------------
# LOAD CREDS FROM STREAMLIT SECRETS
# -----------------------------
creds_info = st.secrets["gcp_service_account"]

credentials = Credentials.from_service_account_info(creds_info, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

client = gspread.authorize(credentials)
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
