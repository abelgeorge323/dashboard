import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- FORCE DARK MODE ----
st.markdown("""
<style>
:root, html[data-theme="light"], html[data-theme="dark"] {
    color-scheme: dark !important;
    --background-color: #0e1016 !important;
    --text-color: #e0e0e0 !important;
    --secondary-bg-color: #151820 !important;
    --primary-color: #4aa8e0 !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}
.js-plotly-plot, .plot-container, canvas, svg {
    background-color: transparent !important;
    color: var(--text-color) !important;
}
h1, h2, h3 {
    color: #dbe3f0 !important;
    text-align: center;
    font-weight: 700;
}
table, th, td {
    background-color: #171b24 !important;
    color: #e1e1e1 !important;
}
.placeholder-box {
    background: #1E1E1E;
    border-radius: 12px;
    padding: 80px;
    text-align: center;
    font-size: 1.2rem;
    color: #bbb;
    box-shadow: 0 0 10px rgba(108, 99, 255, 0.1);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/pub?gid=813046237&single=true&output=csv"
    try:
        df = pd.read_csv(url)
        df = df.dropna(how="all")

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        # Unify naming
        rename_map = {
            "MIT Name": "MIT Name",
            "New Candidate Name": "MIT Name",
            "Start date": "Start Date",
            "Start Date": "Start Date",
            "Training Site": "Training Site",
            "VERT": "VERT",
            "Location": "Location",
            "Salary": "Salary",
            "Level": "Level",
            "Status": "Status",
            "Confidence": "Confidence",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # Filter only relevant rows
        df = df[df["MIT Name"].notna()]

        # Clean salary
        df["Salary"] = (
            df["Salary"].astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .str.replace(" ", "")
        )
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

        # Parse dates
        if "Start Date" in df.columns:
            df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

        # Compute week number
        today = pd.Timestamp.now()
        def calc_weeks(row):
            if pd.isna(row["Start Date"]):
                return None
            if row["Start Date"] > today:
                return 0
            return int(((today - row["Start Date"]).days // 7) + 1)

        df["Week"] = df.apply(calc_weeks, axis=1)

        # Normalize Status
        df["Status"] = df["Status"].astype(str).str.strip().str.lower()

        return df, "Google Sheets"

    except Exception as e:
        st.error(f"⚠️ Error loading MIT tracking data: {e}")
        return pd.DataFrame(), "Error"


@st.cache_data(ttl=300)
def load_jobs_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/pub?gid=1073524035&single=true&output=csv"
    try:
        jobs_df = pd.read_csv(url)
        jobs_df = jobs_df.dropna(how="all")

        # Normalize columns
        jobs_df.columns = [c.strip() for c in jobs_df.columns]
        jobs_df = jobs_df.rename(columns={
            "Job Title": "Job Title",
            "Account": "Account",
            "City": "City",
            "State": "State",
            "Salary": "Salary",
            "VERT": "VERT"
        })

        # Drop irrelevant columns
        jobs_df = jobs_df.drop(columns=[c for c in ["JV Link", "JV ID"] if c in jobs_df.columns], errors="ignore")

        return jobs_df

    except Exception as e:
        st.error(f"⚠️ Error loading Placement Options data: {e}")
        return pd.DataFrame()

# ---- LOAD ----
st.cache_data.clear()
df, data_source = load_data()
jobs_df = load_jobs_data()

if df.empty:
    st.error("❌ Unable to load data.")
    st.stop()

# ---- METRICS ----
offer_pending = len(df[df["Status"] == "offer pending"])
offer_accepted = len(df[df["Status"] == "offer accepted"])
in_training = len(df[df["Status"] == "training"])
ready_for_placement = len(df[df["Status"] == "offer accepted"])

total_candidates = len(df)

open_jobs = len(jobs_df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total_candidates)
col2.metric("Open Positions", open_jobs)
col3.metric("Ready for Placement", ready_for_placement)
col4.metric("In Training", in_training)
col5.metric("Offer Pending", offer_pending)

# ---- CHART ----
st.markdown("---")
left_col, right_col = st.columns([1, 1])
color_map = {
    "Ready for Placement": "#2E91E5",
    "In Training": "#E15F99",
    "Offer Pending": "#A020F0",
}
chart_data = pd.DataFrame({
    "Category": ["Ready for Placement", "In Training", "Offer Pending"],
    "Count": [ready_for_placement, in_training, offer_pending]
})

with right_col:
    st.subheader("📊 Candidate Status Overview")
    fig_pie = px.pie(
        chart_data, names="Category", values="Count", hole=0.45,
        color="Category", color_discrete_map=color_map
    )
    fig_pie.update_traces(textinfo='percent+label', textposition='inside')
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="white", 
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        st.dataframe(jobs_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)
