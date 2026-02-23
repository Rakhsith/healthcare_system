import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Patient Flow Sankey", layout="wide")

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

.section-title {
    font-size: 1.2rem; 
    font-weight: 700; 
    color: var(--text);
    margin-top: 24px; 
    margin-bottom: 16px;
    padding-bottom: 12px; 
    border-bottom: 2px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>🔄 Patient Flow Analysis</h1>
    <p>Sankey Diagram - Patient Journey Through Hospital</p>
</div>
""", unsafe_allow_html=True)

try:
    # Load data
    if 'session_data' in globals() and session_data is not None:
        if isinstance(session_data, pd.DataFrame):
            df = session_data.copy()
        else:
            df = pd.DataFrame(session_data)
    else:
        patients = requests.get("http://127.0.0.1:8000/patients").json()
        df = pd.DataFrame(patients)

    if 'patient_id' not in df.columns and 'id' in df.columns:
        df['patient_id'] = df['id']
    elif 'patient_id' not in df.columns:
        df['patient_id'] = range(1, len(df) + 1)

    # Check for required columns
    has_dept = "department" in df.columns
    has_outcome = "outcome" in df.columns
    
    if has_dept and has_outcome:
        flow = df.groupby(["department","outcome"]).size().reset_index(name="count")
        
        departments = sorted(list(df["department"].unique()))
        outcomes = sorted(list(df["outcome"].unique()))
        
        labels = departments + outcomes
        source = []
        target = []
        value = []
        
        for i, row in flow.iterrows():
            source.append(departments.index(row["department"]))
            target.append(len(departments) + outcomes.index(row["outcome"]))
            value.append(row["count"])
        
        # Color mapping
        colors = []
        for i, dept in enumerate(departments):
            colors.append("rgba(124, 58, 237, 0.8)")
        for i, outcome in enumerate(outcomes):
            if "discharge" in str(outcome).lower():
                colors.append("rgba(16, 185, 129, 0.8)")
            elif "readmit" in str(outcome).lower():
                colors.append("rgba(239, 68, 68, 0.8)")
            else:
                colors.append("rgba(6, 182, 212, 0.8)")
        
        link_colors = []
        for s in source:
            link_colors.append("rgba(124, 58, 237, 0.3)")
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                label=labels,
                color=colors,
                customdata=labels,
                hovertemplate='%{customdata}<br>Patients: %{value}<extra></extra>'
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors,
                hovertemplate='%{source.label} → %{target.label}<br>Patients: %{value}<extra></extra>'
            )
        )])
        
        fig.update_layout(
            font=dict(size=12, color="#e6eef8"),
            height=600,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.markdown("<div class='section-title'>📊 Flow Statistics</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patients", len(df), "Active Records")
        with col2:
            st.metric("Departments", len(departments))
        with col3:
            st.metric("Outcomes", len(outcomes))
        
        # Data tables
        st.markdown("<div class='section-title'>📈 Department-Outcome Matrix</div>", unsafe_allow_html=True)
        pivot_table = df.groupby(["department", "outcome"]).size().unstack(fill_value=0)
        st.dataframe(pivot_table, use_container_width=True)
        
        st.markdown("<div class='section-title'>📊 Department Statistics</div>", unsafe_allow_html=True)
        dept_stats = df.groupby("department").agg({
            "patient_id": "count",
        }).round(2)
        if "treatment_cost" in df.columns:
            dept_stats["Avg Cost"] = df.groupby("department")["treatment_cost"].mean()
        if "age" in df.columns:
            dept_stats["Avg Age"] = df.groupby("department")["age"].mean()
        dept_stats.columns = ["Total Patients"] + list(dept_stats.columns[1:])
        st.dataframe(dept_stats, use_container_width=True)
    else:
        st.warning("⚠️ Missing required columns")
        st.info("""
        💡 This page requires 'department' and 'outcome' columns in your data.
        
        **Available columns:**""" + ", ".join([f"`{c}`" for c in df.columns.tolist()[:10]]))
        st.markdown("Please upload a healthcare dataset with department and patient outcome information.")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Make sure the backend server is running or upload healthcare data in the sidebar")

try:
    if 'session_data' in globals() and session_data is not None:
        if isinstance(session_data, pd.DataFrame):
            df = session_data.copy()
        else:
            df = pd.DataFrame(session_data)
    else:
        patients = requests.get("http://127.0.0.1:8000/patients").json()
        df = pd.DataFrame(patients)

    if 'patient_id' not in df.columns:
        df = df.copy()
        df['patient_id'] = range(1, len(df) + 1)

    if "department" in df.columns and "outcome" in df.columns:
        flow = df.groupby(["department","outcome"]).size().reset_index(name="count")
        
        departments = sorted(list(df["department"].unique()))
        outcomes = sorted(list(df["outcome"].unique()))
        
        labels = departments + outcomes
        source = []
        target = []
        value = []
        
        for i, row in flow.iterrows():
            source.append(departments.index(row["department"]))
            target.append(len(departments) + outcomes.index(row["outcome"]))
            value.append(row["count"])
        
        # Color mapping
        colors = []
        for i, dept in enumerate(departments):
            colors.append("rgba(102, 126, 234, 0.8)")
        for i, outcome in enumerate(outcomes):
            if outcome == "Discharged":
                colors.append("rgba(16, 185, 129, 0.8)")
            elif outcome == "Readmitted":
                colors.append("rgba(239, 68, 68, 0.8)")
            else:
                colors.append("rgba(245, 158, 11, 0.8)")
        
        link_colors = []
        for s in source:
            if s < len(departments):
                link_colors.append("rgba(102, 126, 234, 0.4)")
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                label=labels,
                color=colors,
                customdata=labels,
                hovertemplate='%{customdata}<br>Count: %{value}<extra></extra>'
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors,
                hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>'
            )
        )])
        
        fig.update_layout(
            font=dict(size=12, family="Arial"),
            height=600,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📊 Total Patients: **{len(df):,}**")
        with col2:
            st.success(f"🏥 Total Departments: **{len(departments)}**")
        with col3:
            st.warning(f"📋 Total Outcomes: **{len(outcomes)}**")
        
        st.markdown("---")
        
        st.markdown("### 📈 Department-Outcome Matrix")
        pivot_table = df.groupby(["department", "outcome"]).size().unstack(fill_value=0)
        st.dataframe(pivot_table, use_container_width=True)
        
        st.markdown("### 📊 Department Statistics")
        dept_stats = df.groupby("department").agg({
            "patient_id": "count",
            "treatment_cost": "mean",
            "age": "mean"
        }).round(2)
        dept_stats.columns = ["Total Patients", "Avg Treatment Cost", "Avg Age"]
        st.dataframe(dept_stats, use_container_width=True)
    else:
        st.warning("Required columns (department, outcome) not found in data")

except Exception as e:
    st.error(f"Unable to connect to backend API: {str(e)}")
    st.info("Make sure the backend server is running on http://127.0.0.1:8000")