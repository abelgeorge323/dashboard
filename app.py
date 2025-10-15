import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        /* Force dark mode globally */
        :root {
            color-scheme: dark;
        }
        html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        /* Prevent light mode flashing */
        * {
            color-scheme: dark !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            color: white;
        }
        section[data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
        }
        /* Force all text elements to light color */
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #FAFAFA !important;
        }
        .dashboard-title {
            font-size: clamp(1.6rem, 3.2vw, 2.3rem);
            font-weight: 700;
            color: white;
            background: linear-gradient(90deg, #6C63FF, #00B4DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        div[data-testid="stMetric"] {
            background: #1E1E1E;
            border-radius: 15px;
            padding: 20px 25px;
            box-shadow: 0 0 12px rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF;
            transition: 0.3s ease;
            min-width: 220px;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 0 25px rgba(108, 99, 255, 0.5);
            transform: scale(1.03);
        }
        div[data-testid="stMetricValue"] {
            color: white !important;
            font-size: clamp(22px, 2.2vw, 30px) !important;
            font-weight: bold !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #E5E7EB !important;
            font-size: clamp(12px, 1.2vw, 14px) !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        /* Force label/value color across browsers and themes */
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #F3F4F6 !important;
            -webkit-text-fill-color: #F3F4F6 !important;
            mix-blend-mode: normal !important;
            opacity: 1 !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
        /* Help icon inside metrics */
        div[data-testid="stMetric"] svg path { fill: #E5E7EB !important; }
        @media (max-width: 1400px) {
            div[data-testid="stMetric"] { min-width: 200px; padding: 18px 20px; }
        }
        @media (max-width: 1100px) {
            div[data-testid="stMetric"] { min-width: 170px; padding: 16px 18px; }
        }
        h3, h4 {
            color: white !important;
            font-weight: 600;
        }
        .insights-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
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
        .status-box {
            background: #1E1E1E;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #6C63FF;
        }
        .algorithm-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border-left: 6px solid #00B4DB;
            box-shadow: 0 0 10px rgba(0, 180, 219, 0.15);
        }
        .match-score-green { color: #4CAF50; }
        .match-score-yellow { color: #FFC107; }
        .match-score-red { color: #F44336; }
    </style>
""", unsafe_allow_html=True)

# ---- DATA LOADING FUNCTIONS ----
@st.cache_data(ttl=300)
def load_active_roster():
    """Load and process MIT tracking data from Google Sheets"""
    # First URL - MIT Tracking for Placement (Active Roster)
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/pub?gid=813046237&single=true&output=csv"
    
    try:
        st.markdown('<div class="status-box">🔄 Loading MIT candidate data from Google Sheets...</div>', unsafe_allow_html=True)
        
        # Load the data - no skiprows needed based on the actual data structure
        df = pd.read_csv(url)
        st.markdown('<div class="status-box">✅ Successfully loaded MIT candidate data!</div>', unsafe_allow_html=True)
        
        # Clean up the data
        df = df.dropna(how='all')
        
        # Process the top section (Training info) - rows with MIT Count
        main_df = df[df['MIT Count'].notna()].copy()
        
        # Filter out "Position Identified" candidates (case-insensitive)
        main_df = main_df[~main_df['Status'].str.contains('Position Identified', case=False, na=False)]
        
        # Process the bottom section (MIT Entering the Program) - rows without MIT Count
        entering_df = df[df['MIT Count'].isna() & df['New Candidate Name'].notna()].copy()
        
        # Clean column names
        main_df.columns = [c.strip() if isinstance(c, str) else c for c in main_df.columns]
        entering_df.columns = [c.strip() if isinstance(c, str) else c for c in entering_df.columns]
        
        # Convert Start date to datetime for both sections
        if 'Start date' in main_df.columns:
            main_df['Start Date'] = pd.to_datetime(main_df['Start date'], errors='coerce')
        if 'Start Date' in entering_df.columns:
            entering_df['Start Date'] = pd.to_datetime(entering_df['Start Date'], errors='coerce')
        
        # Calculate weeks for main section
        today = pd.Timestamp.now()
        def calculate_weeks(row):
            start = row.get('Start Date')
            if pd.isna(start):
                return None
            if start > today:
                days_until = (start - today).days
                weeks_until = days_until / 7
                return f"-{int(weeks_until)} weeks from start"
            else:
                days_since = (today - start).days
                week_number = (days_since // 7) + 1
                return int(week_number)
        
        main_df['Week'] = main_df.apply(calculate_weeks, axis=1)
        
        # For entering section, calculate if they're starting in the future
        entering_df['Week'] = entering_df.apply(calculate_weeks, axis=1)
        
        # Handle salary formatting
        for df_section in [main_df, entering_df]:
            if 'Salary' in df_section.columns:
                df_section['Salary'] = df_section['Salary'].astype(str).str.replace('$', '').str.replace(',', '').str.replace(' ', '')
                df_section['Salary'] = pd.to_numeric(df_section['Salary'], errors='coerce')
        
        # Map vertical codes to full names
        vertical_map = {
            'MANU': 'Manufacturing',
            'AUTO': 'Automotive',
            'FIN': 'Finance',
            'TECH': 'Technology',
            'AVI': 'Aviation',
            'DIST': 'Distribution',
            'RD': 'R&D',
            'Reg & Div': 'Regulatory & Division'
        }
        
        for df_section in [main_df, entering_df]:
            if 'VERT' in df_section.columns:
                df_section['Vertical Full'] = df_section['VERT'].map(vertical_map).fillna(df_section['VERT'])
        
        return main_df, entering_df
        
    except Exception as e:
        st.error(f"Error loading MIT candidate data: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def load_placement_options():
    """Load open job positions from Google Sheets"""
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTAdbdhuieyA-axzb4aLe8c7zdAYXBLPNrIxKRder6j1ZAlj2g4U1k0YzkZbm_dEcSwBik4CJ57FROJ/pub?gid=1073524035&single=true&output=csv"
    
    try:
        st.markdown('<div class="status-box">🔄 Loading job positions from Google Sheets...</div>', unsafe_allow_html=True)
        
        # Load the data - skip first 5 rows to get to actual headers
        df = pd.read_csv(url, skiprows=5)
        st.markdown('<div class="status-box">✅ Successfully loaded job positions!</div>', unsafe_allow_html=True)
        
        # Drop unnecessary columns
        df = df.drop(['JV ID', 'JV Link'], axis=1, errors='ignore')
        
        # Clean up the data
        df = df.dropna(how='all')
        
        # Remove rows where Job Title is empty
        if 'Job Title' in df.columns:
            df = df.dropna(subset=['Job Title'])
            df = df[df['Job Title'].str.strip() != '']
        
        # Map VERT codes to full names for jobs
        vertical_map = {
            'MANU': 'Manufacturing',
            'AUTO': 'Automotive',
            'FIN': 'Finance',
            'TECH': 'Technology',
            'AVI': 'Aviation',
            'DIST': 'Distribution',
            'RD': 'R&D',
            'LIFSC': 'Life Science',
            'Reg & Div': 'Regulatory & Division'
        }
        
        if 'VERT' in df.columns:
            df['Vertical'] = df['VERT'].map(vertical_map).fillna(df['VERT'])
        
        # Fill NaN values with empty strings for display
        df = df.fillna('')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading job positions: {e}")
        return pd.DataFrame()

# ---- MATCH SCORE ALGORITHM ----
def parse_salary_range(salary_str):
    """Parse salary range string and return average"""
    if pd.isna(salary_str) or salary_str == '':
        return 0
    
    # Handle formats like "70,000 - 75,000" or "65,000-70,000"
    salary_str = str(salary_str).replace(',', '').replace(' ', '')
    
    if '-' in salary_str:
        try:
            parts = salary_str.split('-')
            low = float(parts[0])
            high = float(parts[1])
            return (low + high) / 2
        except:
            return 0
    else:
        try:
            return float(salary_str)
        except:
            return 0

def same_city(location1, location2):
    """Check if two locations are in the same city"""
    if pd.isna(location1) or pd.isna(location2):
        return False
    
    city1 = location1.split(',')[0].strip().lower()
    city2 = location2.split(',')[0].strip().lower()
    return city1 == city2

def same_state(location1, state2):
    """Check if location is in the same state"""
    if pd.isna(location1) or pd.isna(state2):
        return False
    
    if ',' in location1:
        state1 = location1.split(',')[1].strip().lower()
        state2 = state2.strip().lower()
        return state1 == state2
    return False

def calculate_match_score(candidate, job):
    """
    Calculate match score between candidate and job position
    Returns score from 0-100
    """
    score = 0
    
    # 1. Vertical Alignment (30 pts + 10 bonus)
    candidate_vert = candidate.get('VERT', '')
    job_vert = job.get('VERT', '')
    
    if candidate_vert == job_vert:
        score += 30
    
    # Bonus for Amazon/Aviation experience
    training_site = candidate.get('Training Site', '')
    if training_site == 'Amazon' or candidate_vert == 'AVI':
        score += 10
    
    # 2. Salary Trajectory (25 pts max)
    candidate_salary = candidate.get('Salary', 0)
    job_salary_avg = parse_salary_range(job.get('Salary', 0))
    
    if job_salary_avg > 0 and candidate_salary > 0:
        if job_salary_avg > candidate_salary * 1.05:  # 5%+ increase
            score += 25
        elif job_salary_avg >= candidate_salary * 0.95:  # within 5%
            score += 15
        else:  # decrease
            score += 5
    else:
        score += 10  # neutral if no salary data
    
    # 3. Geographic Fit (20 pts max)
    candidate_location = candidate.get('Location', '')
    job_location = f"{job.get('City', '')}, {job.get('State', '')}"
    
    if same_city(candidate_location, job_location):
        score += 20
    elif same_state(candidate_location, job.get('State', '')):
        score += 10
    else:
        score += 5  # minimal score for different locations
    
    # 4. Confidence Level (15 pts max)
    confidence_map = {'High': 15, 'Moderate': 10, 'Low': 5}
    confidence = candidate.get('Confidence', 'Moderate')
    score += confidence_map.get(confidence, 10)
    
    # 5. Readiness (10 pts max)
    week = candidate.get('Week', 0)
    if isinstance(week, int) and week >= 6:
        score += 10
    elif isinstance(week, int):
        score += max(0, week * 1.5)
    else:
        score += 5  # neutral for non-numeric weeks
    
    return min(int(score), 100)

# ---- MAIN DASHBOARD ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard</div>', unsafe_allow_html=True)

# Load data
main_df, entering_df = load_active_roster()
jobs_df = load_placement_options()

if main_df.empty and entering_df.empty:
    st.error("❌ Unable to load candidate data. Please check the Google Sheet configuration.")
    st.stop()

# Combine all MIT candidates (excluding Position Identified)
all_candidates = []
if not main_df.empty:
    all_candidates.append(main_df)
if not entering_df.empty:
    # Only include Offer Accepted candidates in main count
    offer_accepted = entering_df[entering_df['Status'] == 'Offer Accepted']
    if not offer_accepted.empty:
        all_candidates.append(offer_accepted)

if all_candidates:
    combined_df = pd.concat(all_candidates, ignore_index=True)
else:
    combined_df = pd.DataFrame()

# ---- KEY METRICS ----
total_candidates = len(combined_df) if not combined_df.empty else 0

# Ready for Placement: Week >= 6 AND Status != "Position Identified"
ready_for_placement = 0
if not combined_df.empty:
    ready_for_placement = len(combined_df[
        (combined_df['Week'].apply(lambda x: isinstance(x, int) and x >= 6)) &
        (~combined_df['Status'].str.contains('Position Identified', case=False, na=False))
    ])

# Open Positions
open_positions = len(jobs_df) if not jobs_df.empty else 0

# In Training: Week 1-5 (Status = "Training")
in_training = 0
if not combined_df.empty:
    in_training = len(combined_df[
        (combined_df['Week'].apply(lambda x: isinstance(x, int) and 1 <= x <= 5)) &
        (combined_df['Status'] == 'Training')
    ])

# Starting MIT Program: Status = "Offer Accepted" AND Start Date > Today
starting_program = 0
if not entering_df.empty:
    today = pd.Timestamp.now()
    starting_program = len(entering_df[
        (entering_df['Status'] == 'Offer Accepted') &
        (entering_df['Start Date'] > today)
    ])

# Display metrics
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Candidates",
    total_candidates,
    help="All active MIT candidates (excluding Position Identified)"
)
col2.metric(
    "Ready for Placement",
    ready_for_placement,
    help="Candidates at Week ≥ 6 who are ready for placement"
)
col3.metric(
    "Open Positions",
    open_positions,
    help="Number of active job openings available"
)
col4.metric(
    "In Training",
    in_training,
    help="Candidates actively in training (Weeks 1-5)"
)
col5.metric(
    "Starting MIT Program",
    starting_program,
    help="New candidates with accepted offers starting soon"
)

# ---- OPEN JOB POSITIONS ----
st.markdown("---")
st.markdown("### 📍 Open Job Positions")

if not jobs_df.empty:
    # Create display format
    display_jobs = jobs_df.copy()
    
    # Create position and location columns
    if 'Job Title' in display_jobs.columns and 'Account' in display_jobs.columns:
        display_jobs['Position'] = display_jobs.apply(
            lambda row: f"{row.get('Job Title', 'N/A')} - {row.get('Account', 'N/A')}", 
            axis=1
        )
    
    if 'City' in display_jobs.columns and 'State' in display_jobs.columns:
        display_jobs['Location'] = display_jobs.apply(
            lambda row: f"{row.get('City', 'N/A')}, {row.get('State', 'N/A')}", 
            axis=1
        )
    
    # Show clean columns
    clean_columns = ['Position', 'Location', 'Vertical', 'Salary']
    available_columns = [col for col in clean_columns if col in display_jobs.columns]
    
    if available_columns:
        styled_df = display_jobs[available_columns].copy()
        st.dataframe(
            styled_df, 
            use_container_width=True,
            height=450,
            hide_index=True
        )
    else:
        st.dataframe(display_jobs, use_container_width=True, height=450)
else:
    st.markdown('<div class="placeholder-box">No job positions available</div>', unsafe_allow_html=True)

# ---- READY CANDIDATES ----
if ready_for_placement > 0:
    st.markdown("---")
    st.markdown("### 👥 Ready Candidates")
    
    ready_candidates = combined_df[
        (combined_df['Week'].apply(lambda x: isinstance(x, int) and x >= 6)) &
        (~combined_df['Status'].str.contains('Position Identified', case=False, na=False))
    ]
    
    if not ready_candidates.empty:
        # Use MIT Name from the appropriate column
        name_col = 'MIT Name' if 'MIT Name' in ready_candidates.columns else 'New Candidate Name'
        
        display_cols = [name_col, 'Week', 'Location', 'Vertical Full', 'Salary']
        available_display_cols = [col for col in display_cols if col in ready_candidates.columns]
        
        if available_display_cols:
            ready_display = ready_candidates[available_display_cols].copy()
            
            # Format salary
            if 'Salary' in ready_display.columns:
                ready_display['Salary'] = ready_display['Salary'].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else "TBD"
                )
            
            st.dataframe(ready_display, use_container_width=True, height=300, hide_index=True)
        else:
            st.dataframe(ready_candidates, use_container_width=True, height=300)

# ---- MATCH SCORE ALGORITHM SECTION ----
st.markdown("---")
st.markdown("### 🎯 Candidate-Job Matching Algorithm")

# Algorithm explanation
st.markdown("""
<div class="algorithm-box">
<h4>📊 Match Score Calculation Factors:</h4>
<ul>
<li><b>Vertical Alignment (30 pts + 10 bonus):</b> Same industry = 30pts, Amazon/Aviation experience = +10pts bonus</li>
<li><b>Salary Trajectory (25 pts max):</b> Increase = 25pts, Same range = 15pts, Decrease = 5pts</li>
<li><b>Geographic Fit (20 pts max):</b> Same city = 20pts, Same state = 10pts</li>
<li><b>Confidence Level (15 pts max):</b> High = 15pts, Moderate = 10pts, Low = 5pts</li>
<li><b>Readiness (10 pts max):</b> Week ≥6 = 10pts, else proportional</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Calculate match scores for ready candidates
if ready_for_placement > 0 and open_positions > 0:
    st.markdown("#### 🎯 Candidate Match Scores")
    
    ready_candidates = combined_df[
        (combined_df['Week'].apply(lambda x: isinstance(x, int) and x >= 6)) &
        (~combined_df['Status'].str.contains('Position Identified', case=False, na=False))
    ]
    
    for _, candidate in ready_candidates.iterrows():
        candidate_name = candidate.get('MIT Name', candidate.get('New Candidate Name', 'Unknown'))
        candidate_week = candidate.get('Week', 0)
        
        # Calculate matches for this candidate
        matches = []
        for _, job in jobs_df.iterrows():
            score = calculate_match_score(candidate, job)
            matches.append({
                'Job': f"{job.get('Job Title', 'N/A')} - {job.get('Account', 'N/A')}",
                'Location': f"{job.get('City', 'N/A')}, {job.get('State', 'N/A')}",
                'Vertical': job.get('Vertical', 'N/A'),
                'Score': score
            })
        
        # Sort by score and take top 3
        matches.sort(key=lambda x: x['Score'], reverse=True)
        top_matches = matches[:3]
        
        # Display candidate with expandable matches
        with st.expander(f"👤 {candidate_name} - Ready for Placement (Week {candidate_week})"):
            st.write("**Top 3 Job Matches:**")
            
            for i, match in enumerate(top_matches, 1):
                score = match['Score']
                if score >= 80:
                    color_class = "match-score-green"
                    icon = "🟢"
                elif score >= 60:
                    color_class = "match-score-yellow"
                    icon = "🟡"
                else:
                    color_class = "match-score-red"
                    icon = "🔴"
                
                st.markdown(f"""
                <div class="match-score-{color_class}">
                <b>{i}. {icon} {match['Job']}</b><br>
                📍 {match['Location']} | 🏢 {match['Vertical']} | ⭐ Match Score: {score}/100
                </div>
                """, unsafe_allow_html=True)
                st.write("")
else:
    if ready_for_placement == 0:
        st.info("No candidates are currently ready for placement (Week ≥ 6).")
    if open_positions == 0:
        st.info("No open job positions available for matching.")

# ---- OFFER PENDING SECTION ----
if not entering_df.empty:
    offer_pending_candidates = entering_df[entering_df['Status'] == 'Offer Pending']
    
    if not offer_pending_candidates.empty:
        st.markdown("---")
        st.markdown("### 🤝 Offer Pending Candidates")
        
        # Display offer pending candidates
        display_cols = ['New Candidate Name', 'Training Site', 'Location', 'Level', 'Notes']
        available_display_cols = [col for col in display_cols if col in offer_pending_candidates.columns]
        
        if available_display_cols:
            offer_pending_display = offer_pending_candidates[available_display_cols].copy()
            st.dataframe(offer_pending_display, use_container_width=True, hide_index=True)
        else:
            st.dataframe(offer_pending_candidates, use_container_width=True, hide_index=True)
        
        st.caption(f"{len(offer_pending_candidates)} candidates with pending offers - awaiting final approval/acceptance")

# ---- FOOTER ----
st.markdown("---")
st.caption("🔄 LIVE DATA: Loading from Google Sheets | Auto-refreshes every 5 minutes | Match scores calculated dynamically")
