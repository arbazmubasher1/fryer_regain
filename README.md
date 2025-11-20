# Fryer Regain Trend Dashboard

A Streamlit dashboard analyzing fryer regain data across Johnny & Jugnu branches.

## Features
- Google Sheets live data connection
- Regain 1 vs Regain 2 overlaid trend charts
- Branch, fryer, product filters
- Altair visualizations

## How to run
1. Clone the repo
2. Create a folder named `credentials/`
3. Place your `service_account.json` inside it
4. Create a `.env` file:

GOOGLE_APPLICATION_CREDENTIALS=credentials/service_account.json

5. Install dependencies:
pip install -r requirements.txt

6. Run:
streamlit run app.py
