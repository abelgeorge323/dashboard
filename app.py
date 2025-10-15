import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG (must come FIRST) ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- STYLING OPTIONS FOR BOSS PRESENTATION ----
# 
# OPTION 1: Modern Professional Light Theme (CURRENT)
# Clean, corporate-friendly light theme with blue accents
#
# OPTION 2: Executive Dark Theme (COMMENTED OUT BELOW)
# Sophisticated dark theme with gold accents for executive presentation
#
# OPTION 3: Vibrant Corporate Theme (COMMENTED OUT BELOW) 
# Bold colors with green success indicators and orange highlights
#
# To switch themes: Comment out current theme and uncomment desired theme

# Option 1: Modern Professional Light Theme (CURRENT)


/* Success Messages */
.stSuccess {
    background-color: #ecfdf5 !important;
    border: 1px solid #10b981 !important;
    color: #065f46 !important;
}

/* Remove duplicate mini title */
[data-testid="stHeadingContainer"] h1 + div {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)
# ---- PAGE CONFIG ----

 


# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        :root {
            color-scheme: dark;
        }
        body, .stApp {
            background-color: #0b0e14 !important;
            color: #f5f5f5 !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #f5f5f5 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            color: #bbbbbb !important;
        }
        .stMetric {
            background: #15181e !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 0 15px rgba(108, 99, 255, 0.15);
            text-align: center;
        }
        .data-source {
            background-color: #143d33;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: 500;
            color: #e1e1e1;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
        }
        table {
            background-color: #14171c !important;
            border-collapse: collapse !important;
            width: 100%;
        }
        th {
            background-color: #1f2430 !important;
            color: #e1e1e1 !important;
            font-weight: 600 !important;
            text-transform: uppercase;
        }
        td {
            background-color: #171a21 !important;
            color: #d7d7d7 !important;
            font-size: 0.95rem !important;
            border-top: 1px solid #252a34 !important;
        }
        tr:hover td {
            background-color: #1e2230 !important;
        }
        .pending-title {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #ffd95e !important;
            margin-bottom: 8px !important;
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
        .main-card {
            border: 1px solid rgba(108, 99, 255, 0.15);
            border-radius: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=60)
def load_data():
    main_data_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/"
        "pub?gid=813046237&single=true&output=csv"
    )
    try:
        df = pd.read_csv(main_data_url, skiprows=1)  # Skip header row
        data_source = "Google Sheets"
    except Exception as e:
        st.error(f"⚠️ Google Sheets error: {e}")
        return pd.DataFrame(), "Error"

    df = df.dropna(how="all")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={"Week ": "Week", "Start date": "Start Date"})
    
    # Handle new data structure - filter out empty rows and clean data
    df = df[df["MIT Name"].notna() & (df["MIT Name"] != "")]  # Remove rows without names
    
    
    
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()

    # Only calculate weeks if Week column is empty or has manual values
    # Check if Week column already has values
    if "Week" in df.columns:
        # Convert existing Week values to numeric
        df["Week"] = pd.to_numeric(df["Week"], errors="coerce")
        
        # Only calculate weeks for rows where Week is NaN (empty)
        def calc_weeks(row):
            # If Week already has a value, keep it
            if pd.notna(row["Week"]):
                return row["Week"]
                
            start = row["Start Date"]
            if pd.isna(start):
                return None
            if start > today:
                return f"-{int((start - today).days / 7)} weeks from start"
            return int(((today - start).days // 7) + 1)

        df["Week"] = df.apply(calc_weeks, axis=1)
        df["Week"] = pd.to_numeric(df["Week"], errors="coerce")


    # Handle salary formatting - new format is "$65,000.00"
    if "Salary" in df.columns:
        df["Salary"] = (
            df["Salary"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .str.replace(" ", "")
            .str.replace(".00", "")  # Remove .00 from new format
        )
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df, data_source


@st.cache_data(ttl=300)
def load_jobs_data():
    # ✅ Updated Placement Options Google Sheets URL
    jobs_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/"
        "pub?gid=1073524035&single=true&output=csv"
    )
    try:
        jobs_df = pd.read_csv(jobs_url, skiprows=5, header=0)  # Skip to data rows
        jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains("^Unnamed")]
        jobs_df = jobs_df.drop(columns=[c for c in ["JV Link", "JV ID"] if c in jobs_df.columns], errors="ignore")
        jobs_df = jobs_df.dropna(how="all").fillna("")
        
        # Clean jobs data - remove empty rows
        jobs_df = jobs_df[jobs_df["Job Title"].notna() & (jobs_df["Job Title"] != "")]
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

in_training = len(
    df[df["Status"].str.lower().eq("training") & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)]
)
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total_candidates)
col2.metric("Open Positions", open_jobs)
col3.metric("Ready for Placement", ready)
col4.metric("In Training (Weeks 1–5)", in_training)
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
    "Count": [ready, in_training, offer_pending]
})

with right_col:
    st.subheader("📊 Candidate Status Overview")
    
    # Create horizontal bar chart with all statuses including Offer Pending
    all_status_data = pd.DataFrame({
        "Status": ["Ready for Placement", "In Training", "Offer Pending"],
        "Count": [ready, in_training, offer_pending]
    })
    
    fig_bar = px.bar(
        all_status_data, 
        x="Count", 
        y="Status", 
        orientation='h',
        color="Status", 
        color_discrete_map={
            "Ready for Placement": "#3b82f6",
            "In Training": "#10b981", 
            "Offer Pending": "#f59e0b"
        },
        text="Count"
    )
    
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="#1e293b", 
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.95)",
            font_color="#1e293b",
            font_size=12
        )
    )
    
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig_bar, use_container_width=True)

with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        clean_jobs_df = jobs_df[jobs_df["Job Title"].notna()]
        st.dataframe(clean_jobs_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)

# ==========================================================
# READY FOR PLACEMENT SECTION
# ==========================================================
ready_df = df[
    df["Week"].apply(lambda x: isinstance(x, (int, float)) and x > 6)
    & (~df["Status"].isin(["position identified", "offer pending", "offer accepted"]))
    & (df["Status"].notna())
]

if not ready_df.empty:
    st.markdown("---")
    st.markdown("### 🧩 Ready for Placement Candidates")

    # Select relevant columns dynamically
    ready_cols = [col for col in ["MIT Name", "Training Site", "Location", "Week", "Salary", "Level"] if col in ready_df.columns]
    ready_display = ready_df[ready_cols].copy().fillna("—")

    # Clean salary formatting
    if "Salary" in ready_display.columns:
        ready_display["Salary"] = (
            ready_display["Salary"].astype(str).str.replace("$", "").str.replace(",", "").replace("nan", "TBD")
        )

    # Show table
    st.dataframe(
        ready_display,
        use_container_width=True,
        hide_index=True,
        height=(len(ready_display) * 35 + 60),
    )
    st.caption(f"{len(ready_display)} candidates are ready for placement — week > 6 and not yet placed.")
else:
    st.markdown('<div class="placeholder-box">No candidates currently ready for placement</div>', unsafe_allow_html=True)


# ==========================================================
# IN TRAINING SECTION
# ==========================================================
in_training_df = df[
    df["Status"].str.lower().eq("training")
    & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)
]

if not in_training_df.empty:
    st.markdown("---")
    st.markdown("### 🏋️ In Training (Weeks 1–5)")

    train_cols = [col for col in ["MIT Name", "Training Site", "Location", "Week", "Salary", "Level"] if col in in_training_df.columns]
    train_display = in_training_df[train_cols].copy().fillna("—")

    if "Salary" in train_display.columns:
        train_display["Salary"] = (
            train_display["Salary"].astype(str).str.replace("$", "").str.replace(",", "").replace("nan", "TBD")
        )

    st.dataframe(
        train_display,
        use_container_width=True,
        hide_index=True,
        height=(len(train_display) * 35 + 60),
    )
    st.caption(f"{len(train_display)} candidates currently in training (weeks 1–5).")
else:
    st.markdown('<div class="placeholder-box">No candidates currently in training</div>', unsafe_allow_html=True)

# ==========================================================
# 🎯 CANDIDATE–JOB MATCH SCORE SECTION (Streamlined Executive View)
# ==========================================================
st.markdown("---")
st.markdown("### 🎯 Placement Readiness Breakdown")

# Executive Summary
st.markdown("""
<div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 20px;">
    <h4 style="color: #1e293b; margin-top: 0;">📋 Executive Summary</h4>
    <p style="color: #475569; margin-bottom: 0; line-height: 1.6;">
        The <strong>Placement Readiness Score</strong> is a comprehensive 100-point assessment that evaluates candidate-job compatibility. 
        Scores consider industry alignment (up to 40 points), salary progression potential (25 points), geographic fit (20 points), 
        placement confidence level (15 points), and training readiness (10 points). Higher scores indicate stronger matches 
        between candidates and available positions, helping prioritize placement efforts for optimal outcomes.
    </p>
</div>
""", unsafe_allow_html=True)

# Filter relevant candidates
candidates_df = df[
    df["Status"].isin(["training", "unassigned", "free agent discussing opportunity"])
].copy()
candidates_df = candidates_df.dropna(subset=["MIT Name"])

if not jobs_df.empty and not candidates_df.empty:

    # ---- Salary parsing logic ----

    def parse_salary(s):
        if pd.isna(s):
            return None
        if isinstance(s, (int, float)):
            return float(s)
    
        # Clean string
        s = str(s).replace("$", "").replace(",", "").replace(".00", "").strip()
    
        # Normalize formats like "70,000 - 75,000" or "70k-75k" or "65000"
        s = s.lower().replace("k", "000").replace("–", "-").replace("—", "-").replace("_", "-")
    
        if "-" in s:
            try:
                low, high = s.split("-")
                return (float(low.strip()), float(high.strip()))
            except ValueError:
                return None
        else:
            try:
                return float(s)
            except ValueError:
                return None

    def midpoint(val):
        if isinstance(val, tuple):
            return (val[0] + val[1]) / 2
        return val if isinstance(val, (int, float)) else None


# ---- Apply salary parsing and midpoint logic ----
    jobs_df["SalaryRange"] = jobs_df["Salary"].apply(parse_salary)
    candidates_df["SalaryRange"] = candidates_df["Salary"].apply(parse_salary)
    
    jobs_df["SalaryMid"] = jobs_df["SalaryRange"].apply(midpoint)
    candidates_df["SalaryMid"] = candidates_df["SalaryRange"].apply(midpoint)


    # ---- Calculate match scores (your scoring stays the same) ----
    match_results = []
    for _, c in candidates_df.iterrows():
        for _, j in jobs_df.iterrows():
            subscores = {}

            # 1) Vertical Alignment
            vert_score = 0
            c_vert = str(c.get("VERT", "")).strip().upper()
            j_vert = str(j.get("VERT", j.get("Vertical", ""))).strip().upper()
            if c_vert == j_vert:
                vert_score += 30
            exp_str = " ".join(
                str(c.get(k, "")).lower()
                for k in c.index if any(x in k.lower() for x in ["experience", "notes", "background"])
            )
            if "amazon" in exp_str or "aviation" in exp_str:
                vert_score += 10
            subscores["Vertical"] = vert_score

            # 2) Salary Trajectory
            c_sal, j_sal = c.get("SalaryMid"), j.get("SalaryMid")
            if j_sal and c_sal:
                if j_sal >= 1.05 * c_sal:
                    sal_score = 25
                elif abs(j_sal - c_sal) / c_sal <= 0.05:
                    sal_score = 15
                elif j_sal < 0.95 * c_sal:
                    sal_score = -10
                else:
                    sal_score = 0
            else:
                sal_score = 0
            subscores["Salary"] = sal_score

            # 3) Geographic Fit
            geo_score = 5
            cand_loc = str(c.get("Location", "")).strip().lower()
            job_city = str(j.get("City", "")).strip().lower()
            job_state = str(j.get("State", "")).strip().upper()
            if cand_loc == job_city:
                geo_score = 20
            elif cand_loc.endswith(job_state.lower()):
                geo_score = 10
            subscores["Geo"] = geo_score

            # 4) Confidence
            conf = str(c.get("Confidence", "")).lower()
            if "high" in conf:
                conf_score = 15
            elif "mod" in conf:
                conf_score = 10
            elif "low" in conf:
                conf_score = 5
            else:
                conf_score = 10
            subscores["Confidence"] = conf_score

            # 5) Readiness
            week = c.get("Week")
            if isinstance(week, (int, float)):
                if week >= 6:
                    ready_score = 10
                elif 1 <= week <= 5:
                    ready_score = week * 1.5
                else:
                    ready_score = 5
            else:
                ready_score = 5
            subscores["Readiness"] = ready_score

            total = sum(subscores.values())

            # Safe access for fields that may vary by sheet
            title_val = j.get("Title") or j.get("Job Title") or "—"
            vert_val = j.get("VERT") or j.get("Vertical") or "—"
            acct_val = j.get("Account") or j.get("Job Account") or "—"

            match_results.append({
                "Candidate": c["MIT Name"],
                "Job Account": acct_val,
                "Title": title_val,
                "City": j.get("City", ""),
                "State": j.get("State", ""),
                "VERT": vert_val,
                "Total Score": round(total, 1),
                "Week": c.get("Week"),
                "Status": c.get("Status")
            })

    match_df = pd.DataFrame(match_results)
    match_df = match_df.sort_values("Total Score", ascending=False)

    # Ready first, then training
    match_df["is_ready"] = (match_df["Week"] >= 6).astype(int)
    match_df = match_df.sort_values(["is_ready", "Week", "Total Score"], ascending=[False, False, False])

    # Expanders per candidate (ready auto-expanded)
    for candidate, group in match_df.groupby("Candidate", sort=False):
        week = group["Week"].iloc[0]
        status = "Ready for Placement" if week >= 6 else "In Training"
        color = "🟢" if week >= 6 else "🟡"
        expanded = True if week >= 6 else False

        top_jobs = group.nlargest(3, "Total Score")
        with st.expander(f"{color} {candidate} — {status} (Week {int(week)})", expanded=expanded):
            # iterate with dicts -> no KeyError from spaces/underscores
            for idx, rec in enumerate(top_jobs.to_dict(orient="records"), start=1):
                title = rec.get("Title", "—")
                account = rec.get("Job Account") or rec.get("Job_Account") or rec.get("Account") or "—"
                city = rec.get("City", "")
                state = rec.get("State", "")
                vert = rec.get("VERT", "—")
                score = rec.get("Total Score", 0)

                st.markdown(
                    f"**{idx}. {title} — {account}**  \n"
                    f"📍 {city}, {state} | 🏢 {vert} | ⭐ Match Score: {score}/100"
                )
            st.markdown("---")

else:
    st.markdown(
        '<div class="placeholder-box">No data available to compute match scores</div>',
        unsafe_allow_html=True
    )




# ---- OFFER PENDING SECTION ----
offer_pending_df = df[df["Status"].str.lower() == "offer pending"]
if not offer_pending_df.empty:
    st.markdown("---")
    st.markdown("### 🤝 Offer Pending Candidates")
    display_cols = [c for c in ["MIT Name", "Training Site", "Location", "Level"] if c in offer_pending_df.columns]
    offer_pending_display = offer_pending_df[display_cols].fillna("—")
    st.dataframe(offer_pending_display, use_container_width=True, hide_index=True)
    st.caption(f"{len(offer_pending_display)} candidates with pending offers – awaiting final approval/acceptance")

# ==========================================================
# ALTERNATIVE STYLING OPTIONS FOR BOSS PRESENTATION
# ==========================================================

OPTION 2: Executive Dark Theme
Replace the current styling with this for a sophisticated dark theme:

st.markdown('''
<style>
/* ===== Executive Dark Theme ===== */
:root {
    --primary-bg: #0f172a;
    --secondary-bg: #1e293b;
    --accent-bg: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --accent-color: #fbbf24;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --border-color: #334155;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--primary-bg) !important;
    color: var(--text-primary) !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 8px 24px rgba(251, 191, 36, 0.2) !important;
    transform: translateY(-2px) !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-color) !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
}

h1, h2, h3 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
</style>
''', unsafe_allow_html=True)

"""
OPTION 3: Vibrant Corporate Theme
Replace the current styling with this for bold, energetic colors:

st.markdown('''
<style>
/* ===== Vibrant Corporate Theme ===== */
:root {
    --primary-bg: #ffffff;
    --secondary-bg: #f0fdf4;
    --accent-bg: #dcfce7;
    --text-primary: #166534;
    --text-secondary: #16a34a;
    --accent-color: #ea580c;
    --success-color: #22c55e;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --border-color: #bbf7d0;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--primary-bg) !important;
    color: var(--text-primary) !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
    border: 2px solid var(--success-color) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 16px rgba(34, 197, 94, 0.2) !important;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3) !important;
    transform: translateY(-3px) !important;
    border-color: var(--accent-color) !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-color) !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
}

h1, h2, h3 {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    text-shadow: 2px 2px 4px rgba(34, 197, 94, 0.2) !important;
}
</style>
''', unsafe_allow_html=True)
"""

