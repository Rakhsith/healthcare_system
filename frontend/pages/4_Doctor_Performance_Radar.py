import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Doctor Performance Radar", layout="wide")

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
    <h1>🩺 Doctor Performance Radar</h1>
    <p>Department Performance Metrics & Comparison</p>
</div>
""", unsafe_allow_html=True)

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

    if "department" in df.columns:
        
        # Calculate normalized metrics
        metrics = df.groupby("department").agg({
            "age": "mean",
            "treatment_cost": "mean",
            "patient_id": "count"
        }).reset_index()
        
        metrics.columns = ["Department", "Avg Age", "Avg Cost", "Patient Count"]
        
        # Normalize values for radar chart (0-100 scale)
        metrics["Avg Age Norm"] = (metrics["Avg Age"] / metrics["Avg Age"].max()) * 100
        metrics["Cost Efficiency"] = 100 - (metrics["Avg Cost"] / metrics["Avg Cost"].max()) * 100
        metrics["Patient Volume"] = (metrics["Patient Count"] / metrics["Patient Count"].max()) * 100
        
        # Radar Chart
        st.markdown("### 📊 Department Performance Radar Chart")
        
        fig = go.Figure()
        
        colors = ["#667eea", "#764ba2", "#FF6B6B", "#10B981", "#F59E0B", "#8B5CF6"]

        for idx, row in metrics.iterrows():
            clr = colors[idx % len(colors)]
            fig.add_trace(go.Scatterpolar(
                r=[row["Avg Age Norm"], row["Cost Efficiency"], row["Patient Volume"]],
                theta=["Avg Age Index", "Cost Efficiency", "Patient Volume"],
                fill='toself',
                name=row["Department"],
                line=dict(color=clr),
                fillcolor="rgba(102,126,234,0.18)"
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            height=500,
            hovermode='closest',
            paper_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Performance Metrics Table
        st.markdown("### 📈 Department Performance Metrics")
        
        # Ensure a patient identifier exists
        if "patient_id" not in df.columns:
            df = df.copy()
            df["patient_id"] = range(1, len(df) + 1)

        display_df = df.groupby("department").agg({
            "patient_id": "count",
            "age": "mean",
            "treatment_cost": ["mean", "sum"],
            "readmission": lambda x: (x.astype(str) == "Yes").mean() * 100
        }).round(2)
        
        display_df.columns = ["Total Patients", "Avg Age", "Avg Treatment Cost", "Total Revenue", "Readmission Rate (%)"]
        display_df = display_df.sort_values("Total Patients", ascending=False)
        
        st.dataframe(display_df, use_container_width=True)
        
        st.markdown("---")
        
        # Comparative Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Patients by Department")
            import plotly.express as px
            fig = px.bar(metrics.sort_values("Patient Count", ascending=False), 
                        x="Department", y="Patient Count",
                        color="Patient Count", color_continuous_scale="Blues")
            fig.update_layout(height=400, hovermode='x unified', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Average Treatment Cost by Department")
            fig = px.bar(metrics.sort_values("Avg Cost", ascending=False),
                        x="Department", y="Avg Cost",
                        color="Avg Cost", color_continuous_scale="Reds")
            fig.update_layout(height=400, hovermode='x unified', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Multiple Radar Charts (one per department)
        st.markdown("### 🎯 Individual Department Performance")
        
        selected_dept = st.selectbox("Select Department:", metrics["Department"].unique())
        
        dept_data = metrics[metrics["Department"] == selected_dept].iloc[0]
        
        fig = go.Figure(data=[go.Scatterpolar(
            r=[dept_data["Avg Age Norm"], dept_data["Cost Efficiency"], dept_data["Patient Volume"]],
            theta=["Patient Age Index", "Cost Efficiency", "Volume Index"],
            fill='toself',
            line=dict(color="#667eea"),
            fillcolor="rgba(102, 126, 234, 0.3)"
        )])
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title=f"Performance Profile - {selected_dept}",
            height=500,
            paper_bgcolor="white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Department Stats
        dept_stats = df[df["department"] == selected_dept]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", len(dept_stats))
        with col2:
            st.metric("Avg Age", f"{dept_stats['age'].mean():.1f}")
        with col3:
            st.metric("Avg Treatment Cost", f"₹{dept_stats['treatment_cost'].mean():.0f}")
        with col4:
            if "readmission" in dept_stats.columns:
                readmit = (dept_stats["readmission"].astype(str) == "Yes").mean() * 100
                st.metric("Readmission Rate", f"{readmit:.1f}%")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Make sure the backend server is running or upload healthcare data with 'department' column in the sidebar")