import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Financial Heatmap", layout="wide")

st.markdown("""
<style>
.header-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: var(--text);
    padding: 40px 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
}
.metric-card { background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(5,150,105,0.04)); color:var(--text); }
.metric-value { font-size: 2em; font-weight: bold; margin:10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1>💰 Financial Heatmap Analysis</h1>
    <p>Treatment Costs Across Departments and Demographics</p>
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

    if "department" in df.columns and "treatment_cost" in df.columns:
        
        # Financial Summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = df["treatment_cost"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div>Total Revenue</div>
                <div class="metric-value">₹{int(total_revenue):,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_cost = df["treatment_cost"].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div>Avg Treatment Cost</div>
                <div class="metric-value">₹{int(avg_cost):,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            max_cost = df["treatment_cost"].max()
            st.markdown(f"""
            <div class="metric-card">
                <div>Max Treatment Cost</div>
                <div class="metric-value">₹{int(max_cost):,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            min_cost = df["treatment_cost"].min()
            st.markdown(f"""
            <div class="metric-card">
                <div>Min Treatment Cost</div>
                <div class="metric-value">₹{int(min_cost):,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Heatmap 1: Department x Gender
        if "gender" in df.columns:
            st.markdown("### 🏥 Average Treatment Cost Heatmap (Department × Gender)")
            heatmap_data = df.pivot_table(
                values="treatment_cost",
                index="department",
                columns="gender",
                aggfunc="mean"
            )
            
            fig = px.imshow(heatmap_data,
                           labels=dict(x="Gender", y="Department", color="Avg Cost (₹)"),
                           color_continuous_scale="RdYlGn_r",
                           aspect="auto",
                           text_auto='.0f')
            fig.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Department wise analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💵 Total Revenue by Department")
            dept_revenue = df.groupby("department")["treatment_cost"].sum().sort_values(ascending=False)
            fig = px.bar(x=dept_revenue.values, y=dept_revenue.index,
                        orientation='h', labels={"x": "Total Revenue (₹)", "index": "Department"},
                        color=dept_revenue.values, color_continuous_scale="Viridis")
            fig.update_layout(height=400, hovermode='closest', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Treatment Cost Distribution by Department")
            fig = px.box(df, x="department", y="treatment_cost",
                        labels={"treatment_cost": "Treatment Cost (₹)", "department": "Department"},
                        color_discrete_sequence=["#667eea"])
            fig.update_layout(height=400, hovermode='closest', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Age group analysis
        df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100], 
                                 labels=['<18', '18-35', '35-50', '50-65', '65+'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Average Treatment Cost by Age Group")
            age_cost = df.groupby("age_group")["treatment_cost"].mean().sort_values(ascending=False)
            fig = px.bar(x=age_cost.index, y=age_cost.values,
                        labels={"x": "Age Group", "y": "Average Treatment Cost (₹)"},
                        color=age_cost.values, color_continuous_scale="Blues")
            fig.update_layout(height=400, hovermode='x unified', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Treatment Cost Trend")
            cost_trend = df.groupby("age")["treatment_cost"].mean().reset_index()
            fig = px.line(cost_trend, x="age", y="treatment_cost",
                         labels={"age": "Patient Age", "treatment_cost": "Average Treatment Cost (₹)"},
                         color_discrete_sequence=["#667eea"])
            fig.update_traces(fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.2)')
            fig.update_layout(height=400, hovermode='x unified', showlegend=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 📋 Detailed Financial Summary")
        financial_summary = df.groupby("department").agg({
            "treatment_cost": ["sum", "mean", "min", "max", "count"]
        }).round(2)
        financial_summary.columns = ["Total Revenue", "Avg Cost", "Min Cost", "Max Cost", "Patient Count"]
        st.dataframe(financial_summary, use_container_width=True)

except Exception as e:
    st.error(f"Unable to connect to backend API: {str(e)}")
    st.info("Make sure the backend server is running on http://127.0.0.1:8000")