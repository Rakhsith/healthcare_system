import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Executive Command Center", layout="wide")

# Dark theme CSS
st.markdown("""
<style>
:root {
    --bg-dark: #030812;
    --bg: #0b1020;
    --card: #0f1724;
    --accent: #7c3aed;
    --accent-2: #10b981;
    --accent-3: #06b6d4;
    --text: #e6eef8;
    --muted: #9AA6BD;
    --border: rgba(255,255,255,0.05);
}

html, body, #root, .block-container {
    background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg) 50%, #0a1525 100%) !important;
    color: var(--text) !important;
}

.page-header {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    color: white;
    padding: 40px 32px;
    border-radius: 20px;
    margin-bottom: 32px;
    text-align: center;
    box-shadow: 0 12px 40px rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.3);
}

.page-header h1 {
    font-size: 2.5rem;
    margin: 0;
    font-weight: 800;
    letter-spacing: -1px;
}

.page-header p {
    font-size: 1.05rem;
    margin-top: 8px;
    opacity: 0.95;
}

.metric-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(16,185,129,0.08));
    color: var(--text);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.2);
    transition: all 0.3s ease;
}

.metric-card:hover {
    background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(16,185,129,0.15));
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(124,58,237,0.2);
    border-color: rgba(124,58,237,0.4);
}

.metric-value {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 16px 0 8px 0;
}

.metric-label {
    font-size: 0.9rem;
    color: var(--muted);
    opacity: 0.95;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.metric-change {
    font-size: 0.85rem;
    color: var(--accent-2);
    margin-top: 8px;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text);
    margin-top: 32px;
    margin-bottom: 16px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>📊 Executive Command Center</h1>
    <p>Real-time Healthcare Operations Overview & Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)

try:
    # Prefer uploaded/session data if provided by the main app
    if 'session_data' in globals() and session_data is not None:
        if isinstance(session_data, pd.DataFrame):
            df = session_data.copy()
        else:
            df = pd.DataFrame(session_data)
    else:
        patients = requests.get("http://127.0.0.1:8000/patients").json()
        df = pd.DataFrame(patients)

    # ensure patient_id exists so aggregations work even for uploaded CSVs
    if 'patient_id' not in df.columns:
        df = df.copy()
        df['patient_id'] = range(1, len(df) + 1)

    total_patients = len(df)
    total_revenue = df.get("treatment_cost", pd.Series(dtype=float)).sum() if not df.empty else 0
    readmission_rate = (df["readmission"].astype(str) == "Yes").mean() * 100 if "readmission" in df.columns else 0
    avg_wait_time = 12
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Total Patients</div>
            <div class="metric-value">{total_patients:,}</div>
            <div class="metric-change">📈 +12% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Total Revenue</div>
            <div class="metric-value">₹{int(total_revenue):,.0f}</div>
            <div class="metric-change">📈 +18% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔄 Readmission Rate</div>
            <div class="metric-value">{round(readmission_rate, 1)}%</div>
            <div class="metric-change">📉 -2.3% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Avg Wait Time</div>
            <div class="metric-value">{avg_wait_time} min</div>
            <div class="metric-change">📉 -3.1 min</div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Section
    st.markdown("<div class='section-title'>📈 Analytics & Insights</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("**Admissions by Department**")
        if "department" in df.columns:
            dept_data = df.groupby("department").size().reset_index(name="count").sort_values("count", ascending=False)
            fig = px.area(dept_data, x="department", y="count", 
                         color_discrete_sequence=["#7c3aed"],
                         labels={"count": "Admissions", "department": "Department"})
            fig.update_traces(fillcolor="rgba(124,58,237,0.2)")
            fig.update_layout(
                height=380, 
                hovermode='x unified', 
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6eef8"),
                xaxis_title="Department",
                yaxis_title="Admissions"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Patient Outcomes Distribution**")
        if "outcome" in df.columns:
            outcome_data = df["outcome"].value_counts().reset_index()
            outcome_data.columns = ["Outcome", "Count"]
            colors = ["#10b981", "#ef4444", "#f59e0b", "#06b6d4"]
            fig = px.pie(outcome_data, values="Count", names="Outcome", 
                        color_discrete_sequence=colors[:len(outcome_data)])
            fig.update_layout(
                height=380, 
                showlegend=True,
                font=dict(color="#e6eef8"),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("**Gender Distribution**")
        if "gender" in df.columns:
            gender_data = df["gender"].value_counts().reset_index()
            gender_data.columns = ["Gender", "Count"]
            fig = px.bar(gender_data, x="Gender", y="Count", 
                        color="Gender", 
                        color_discrete_map={"M": "#7c3aed", "F": "#06b6d4", "Other": "#10b981"})
            fig.update_layout(
                height=380, 
                hovermode='x unified',
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6eef8"),
                xaxis_title="Gender",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Revenue by Department (Top 10)**")
        if "department" in df.columns and "treatment_cost" in df.columns:
            revenue_data = df.groupby("department")["treatment_cost"].sum().reset_index().sort_values("treatment_cost", ascending=False).head(10)
            revenue_data.columns = ["Department", "Revenue"]
            fig = px.bar(revenue_data, y="Department", x="Revenue",
                         orientation='h', 
                         color_discrete_sequence=["#10b981"],
                         labels={"Revenue": "Revenue (₹)", "Department": "Department"})
            fig.update_layout(
                height=380, 
                hovermode='closest', 
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6eef8"),
                yaxis_title="Department"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Preview
    st.markdown("<div class='section-title'>📋 Recent Patient Records</div>", unsafe_allow_html=True)
    with st.expander("📊 View Data", expanded=True):
        st.dataframe(df.head(15), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Make sure the backend server is running on http://127.0.0.1:8000 or upload data in the sidebar")
