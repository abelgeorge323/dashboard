# MIT Candidate Training Dashboard

A sleek, executive-facing dashboard that reads live data from Google Sheets, calculates intelligent candidate-job match scores, and presents information in an intuitive dark-mode interface.

## Features

- **Live Data Integration**: Automatically syncs with Google Sheets
- **Smart Matching Algorithm**: Calculates match scores based on vertical alignment, salary trajectory, geographic fit, confidence level, and readiness
- **Executive Dashboard**: Clean, dark-mode interface optimized for leadership
- **Real-time Updates**: Data refreshes every 5 minutes
- **Responsive Design**: Works on desktop, tablet, and mobile

## Metrics Tracked

1. **Total Candidates**: All active MIT candidates (excluding Position Identified)
2. **Ready for Placement**: Candidates at Week ≥ 6 who are ready for placement
3. **Open Positions**: Number of active job openings available
4. **In Training**: Candidates actively in training (Weeks 1-5)
5. **Starting MIT Program**: New candidates with accepted offers starting soon

## Data Sources

- **Active Roster**: Google Sheets with MIT candidate tracking
- **Placement Options**: Google Sheets with open job positions

## Match Score Algorithm

The algorithm calculates scores (0-100) based on:

- **Vertical Alignment (30 pts + 10 bonus)**: Same industry = 30pts, Amazon/Aviation experience = +10pts
- **Salary Trajectory (25 pts max)**: Increase = 25pts, Same range = 15pts, Decrease = 5pts
- **Geographic Fit (20 pts max)**: Same city = 20pts, Same state = 10pts
- **Confidence Level (15 pts max)**: High = 15pts, Moderate = 10pts, Low = 5pts
- **Readiness (10 pts max)**: Week ≥6 = 10pts, else proportional

## Deployment

This dashboard is deployed on Streamlit Cloud and automatically updates when the underlying Google Sheets are modified.

## Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Data Source**: Google Sheets (CSV export)
