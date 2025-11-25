import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import altair as alt

# Streamlit Page Setup
st.set_page_config(page_title="Fryer Regain Trend Dashboard", layout="wide")
st.title("🔥 Fryer Regain Trend Dashboard (Google Sheets Connected)")

# -----------------------------
# 1. LOAD GOOGLE SERVICE ACCOUNT FROM STREAMLIT SECRETS
# -----------------------------
try:
    creds_info = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Missing [gcp_service_account] block in Streamlit Secrets.\n\n"
             "Go to https://share.streamlit.io → App Settings → Secrets "
             "and paste your service account.")
    st.stop()

credentials = Credentials.from_service_account_info(
    creds_info,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

client = gspread.authorize(credentials)

# -----------------------------
# 2. GOOGLE SHEET URL
# -----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/14r53FBraAalBclaecplACdvI7vmUctEQDl2Ewv7Pdho/edit#gid=0"

try:
    sheet = client.open_by_url(sheet_url).sheet1
    raw_data = sheet.get_all_records()
    df = pd.DataFrame(raw_data)
    st.success("Google Sheet successfully loaded!")
except Exception as e:
    st.error(f"Error loading Google Sheet:\n\n{e}")
    st.stop()

# -----------------------------
# 3. CLEAN & PREPARE DATA
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Regain Seconds"] = pd.to_numeric(df["Regain Seconds"], errors="coerce")

df = df.sort_values(["Fryer ID", "Product", "Date", "Regain Type"])

# -----------------------------
# 4. SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

branches = st.sidebar.multiselect("Filter by Branch", df["Branch"].unique(), df["Branch"].unique())
fryers = st.sidebar.multiselect("Filter by Fryer ID", df["Fryer ID"].unique(), df["Fryer ID"].unique())
products = st.sidebar.multiselect("Filter by Product", df["Product"].unique(), df["Product"].unique())

filtered = df[
    df["Branch"].isin(branches) &
    df["Fryer ID"].isin(fryers) &
    df["Product"].isin(products)
]

# -----------------------------
# 5. OVERLAID CHARTS: REGAIN 1 VS REGAIN 2
# -----------------------------
st.subheader("📊 Overlaid Regain 1 vs Regain 2 Trend for Each Fryer")

if filtered.empty:
    st.warning("No data found for selected filters.")
else:
    for fryer in filtered["Fryer ID"].unique():
        fryer_df = filtered[filtered["Fryer ID"] == fryer]

        chart = (
            alt.Chart(fryer_df)
            .mark_line(point=True)
            .encode(
                x="Date:T",
                y="Regain Seconds:Q",
                color="Regain Type:N",
                tooltip=["Date", "Branch", "Fryer ID", "Product", "Regain Type", "Regain Seconds"]
            )
            .properties(
                title=f"Fryer: {fryer}",
                width=900,
                height=300
            )
        )

        st.altair_chart(chart, use_container_width=True)

# -----------------------------
# 5B. SEPARATE BRANCH-WISE CHARTS
# -----------------------------
st.subheader("🏭 Branch-Wise Regain Trends")

if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    for branch in filtered["Branch"].unique():
        st.markdown(f"### ⭐ Branch: **{branch}**")

        branch_df = filtered[filtered["Branch"] == branch]

        for fryer in branch_df["Fryer ID"].unique():
            fryer_df = branch_df[branch_df["Fryer ID"] == fryer]

            chart = (
                alt.Chart(fryer_df)
                .mark_line(point=True)
                .encode(
                    x="Date:T",
                    y="Regain Seconds:Q",
                    color="Regain Type:N",
                    tooltip=["Date", "Branch", "Fryer ID", "Product", "Regain Type", "Regain Seconds"]
                )
                .properties(
                    title=f"{branch} — Fryer {fryer}",
                    width=900,
                    height=300
                )
            )

            st.altair_chart(chart, use_container_width=True)

# -----------------------------
# 6. RAW DATA TABLE
# -----------------------------
st.subheader("📋 Raw Data")
st.dataframe(filtered)
