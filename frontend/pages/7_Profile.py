import streamlit as st
import datetime

st.set_page_config(page_title="User Profile", layout="wide")

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

.profile-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(16,185,129,0.08));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(124,58,237,0.1);
}

.profile-section {
    background: rgba(15,23,36,0.8);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}

.profile-field {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

.profile-field-label {
    font-weight: 600;
    color: var(--muted);
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.profile-field-value {
    color: var(--text);
    font-size: 1.05rem;
    font-weight: 500;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-top: 24px;
}

.stat-box {
    background: rgba(15,23,36,0.6);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: var(--muted);
    font-size: 0.85rem;
    margin-top: 8px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h1>👤 User Profile</h1>
    <p>Account Settings & Personal Information</p>
</div>
""", unsafe_allow_html=True)

# Check if user is authenticated
if "user" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("⚠️ Please log in to view your profile")
    st.stop()

username = st.session_state.get("user", "Unknown User")
login_time = st.session_state.get("login_time")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    <div style='
        width: 140px;
        height: 140px;
        background: linear-gradient(135deg, #7c3aed 0%, #10b981 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        box-shadow: 0 8px 24px rgba(124,58,237,0.3);
    '>
        🧑‍⚕️
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='profile-card'>
        <div style='font-size: 1.5rem; font-weight: 700; color: var(--text); margin-bottom: 8px;'>{username}</div>
        <div style='color: var(--text-secondary); font-size: 0.95rem;'>Healthcare Administrator</div>
        <div style='color: var(--muted); font-size: 0.85rem; margin-top: 12px;'>✓ Active Account</div>
    </div>
    """, unsafe_allow_html=True)

# Account Information
st.markdown("### Account Information")
st.markdown("""
<div class='profile-section'>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class='profile-field'>
        <span class='profile-field-label'>Username</span>
        <span class='profile-field-value'>{username}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='profile-field'>
        <span class='profile-field-label'>Account Type</span>
        <span class='profile-field-value'>Administrator</span>
    </div>
    """, unsafe_allow_html=True)

if login_time:
    try:
        login_dt = datetime.datetime.fromisoformat(login_time)
        login_str = login_dt.strftime("%B %d, %Y • %H:%M:%S")
    except:
        login_str = login_time
else:
    login_str = "Not available"

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class='profile-field'>
        <span class='profile-field-label'>Last Login</span>
        <span class='profile-field-value'>{login_str}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='profile-field'>
        <span class='profile-field-label'>Status</span>
        <span class='profile-field-value' style='color: #10b981;'>🟢 Online</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Usage Statistics
st.markdown("### Usage Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-value'>6</div>
        <div class='stat-label'>Pages</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-value'>∞</div>
        <div class='stat-label'>Datasets</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-value'>4</div>
        <div class='stat-label'>Export Formats</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-value'>100%</div>
        <div class='stat-label'>Uptime</div>
    </div>
    """, unsafe_allow_html=True)

# Features & Permissions
st.markdown("### Features & Permissions")
st.markdown("""
<div class='profile-section'>
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>
        <div style='padding: 12px; color: #10b981;'>✓ Dashboard Access</div>
        <div style='padding: 12px; color: #10b981;'>✓ Analytics Reports</div>
        <div style='padding: 12px; color: #10b981;'>✓ Data Upload</div>
        <div style='padding: 12px; color: #10b981;'>✓ Export Reports</div>
        <div style='padding: 12px; color: #10b981;'>✓ Timeline Analysis</div>
        <div style='padding: 12px; color: #10b981;'>✓ Performance Metrics</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Data Management
st.markdown("### Data Management")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download My Data", use_container_width=True):
        st.info("💾 Data export would include all your uploaded datasets and analysis history")

with col2:
    if st.button("🔄 Sync Settings", use_container_width=True):
        st.success("✓ Settings synchronized across all devices")

# Footer
st.markdown("""
<div style='text-align: center; padding: 32px 0; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.05);'>
    <div style='color: var(--muted); font-size: 0.9rem;'>MedIntel X • Premium Healthcare Analytics</div>
    <div style='color: var(--muted); font-size: 0.8rem; margin-top: 8px;'>Profile • Account Security • Data Privacy</div>
</div>
""", unsafe_allow_html=True)
