import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- CUSTOM STYLING ----
st.markdown("""
<style>
:root { color-scheme: dark; }
body, .stApp { background-color: #0b0e14 !important; color: #f5f5f5 !important; }
h1, h2, h3, h4, h5, h6, p, span, div { color: #f5f5f5 !important; }
div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { font-size: 1rem !important; color: #bbbbbb !important; }
.stMetric { background: #15181e !important; border-radius: 16px !important;
            padding: 24px !important; box-shadow: 0 0 15px rgba(108,99,255,0.15); text-align: center; }
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important;
                              box-shadow: 0 0 10px rgba(108,99,255,0.15); }
table { background-color: #14171c !important; width: 100%; border-collapse: collapse !important; }
th { background-color: #1f2430 !important; color: #e1e1e1 !important; text-transform: uppercase; }
td { background-color: #171a21 !important; color: #d7d7d7 !important;
     font-size: 0.95rem !important; border-top: 1px solid #252a34 !important; }
tr:hover td { background-color: #1e2230 !important; }
.placeholder-box { background: #1E1E1E; border-radius: 12px; padding: 80px;
                   text-align: center; font-size: 1.2rem; color: #bbb;
                   box-shadow: 0 0 10px rgba(108,99,255,0.1); }
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    main_data_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=1155015355&single=true&output=csv"
    try:
        df = pd.read_csv(main_data_url, skiprows=4)
        data_source = "Google Sheets"
    except Exception as e:
        st.error(f"⚠️ Google Sheets error: {e}")
        return pd.DataFrame(), "Error"

    df = df.dropna(how="all")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={"Week ": "Week", "Start date": "Start Date"})
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()
    def calc_weeks(row):
        start = row["Start Date"]
        if pd.isna(start): return None
        if start > today: return f"-{int((start - today).days / 7)} weeks from start"
        return int(((today - start).days // 7) + 1)
    df["Week"] = df.apply(calc_weeks, axis=1)

    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df, data_source


@st.cache_data(ttl=300)
def load_jobs_data():
    jobs_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=116813539&single=true&output=csv"
    try:
        jobs_df = pd.read_csv(jobs_url, skiprows=5, header=0)
        jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains("^Unnamed")]
        jobs_df = jobs_df.dropna(how="all").fillna("")
        return jobs_df
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return pd.DataFrame()


# ---- LOAD ----
df, data_source = load_data()
jobs_df = load_jobs_data()

if df.empty:
    st.error("❌ Unable to load data.")
    st.stop()

# ---- HEADER ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard</div>', unsafe_allow_html=True)
if data_source == "Google Sheets":
    st.success(f"📊 Data Source: {data_source} | Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---- METRICS ----
offer_pending = len(df[df["Status"] == "offer pending"])
offer_accepted = len(df[df["Status"] == "offer accepted"])
non_identified = len(df[df["Status"].isin(["free agent discussing opportunity", "unassigned", "training"])])
total_candidates = non_identified + offer_accepted
ready_for_placement = df[
    df["Week"].apply(lambda x: isinstance(x, (int, float)) and x > 6)
    & (~df["Status"].isin(["position identified", "offer pending", "offer accepted"]))
]
ready = len(ready_for_placement)
in_training = len(df[df["Status"].eq("training")
                    & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)])
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total_candidates)
col2.metric("Open Positions", open_jobs)
col3.metric("Ready for Placement", ready)
col4.metric("In Training (Weeks 1–5)", in_training)
col5.metric("Offer Pending", offer_pending)

# ---- CHARTS ----
st.markdown("---")
left_col, right_col = st.columns([1, 1])
chart_data = pd.DataFrame({
    "Category": ["Ready for Placement", "In Training", "Offer Pending"],
    "
