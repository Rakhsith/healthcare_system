import os
import sqlite3
import hashlib
import datetime
import runpy
import streamlit as st
import pandas as pd
import requests
from streamlit_option_menu import option_menu

st.set_page_config(page_title="MedIntel X", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS / Theme ----------
def load_css():
    css = """
    <style>
    :root {
        --bg-dark: #030812;
        --bg: #0b1020;
        --bg-light: #11192a;
        --card: #0f1724;
        --card-hover: #131d2d;
        --muted: #9AA6BD;
        --accent: #7c3aed;
        --accent-2: #10b981;
        --accent-3: #06b6d4;
        --text: #e6eef8;
        --text-secondary: #b0bac9;
        --border: rgba(255,255,255,0.05);
    }
    
    html, body, #root, .block-container {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg) 50%, #0a1525 100%) !important;
        color: var(--text) !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #030812 0%, #0a1422 50%, #0f1724 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: var(--text) !important;
    }
    
    /* Cards & Containers */
    .card {
        background: linear-gradient(135deg, rgba(15,23,36,0.8), rgba(11,16,32,0.6));
        border: 1px solid var(--border);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        color: var(--text);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        background: linear-gradient(135deg, rgba(15,23,36,0.95), rgba(11,16,32,0.75));
        border-color: rgba(124,58,237,0.2);
        box-shadow: 0 12px 48px rgba(124,58,237,0.1);
    }
    
    /* Brand & Text */
    .brand-badge { 
        font-weight:700; 
        font-size:1.3rem; 
        letter-spacing: 1px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .auth-title { 
        font-size:2rem; 
        font-weight:700; 
        color:var(--text);
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    
    .auth-subtitle { 
        color:var(--muted); 
        margin-bottom:20px;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .small-muted { 
        color:var(--muted); 
        font-size:0.9rem;
    }
    
    /* Metric Cards */
    .metric-card { 
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(16,185,129,0.08));
        border: 1px solid rgba(124,58,237,0.3);
        padding: 24px;
        border-radius: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(124,58,237,0.1);
    }
    
    .metric-card:hover {
        background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(16,185,129,0.15));
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(124,58,237,0.2);
        border-color: rgba(124,58,237,0.5);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 12px 0 6px 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-subtitle {
        font-size: 0.85rem;
        color: var(--muted);
        margin-top: 8px;
    }
    
    /* Auth Enhancements */
    .auth-container { 
        padding: 40px 32px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1.5px solid var(--border);
        background: linear-gradient(135deg, rgba(15,23,36,0.95), rgba(11,16,32,0.8));
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }
    
    .glass-hero { 
        background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(16,185,129,0.12), rgba(6,182,212,0.08));
        border: 1.5px solid var(--border);
        padding: 48px 40px;
        border-radius: 24px;
        box-shadow: 0 16px 48px rgba(124,58,237,0.15);
        margin-bottom: 32px;
        text-align: center;
    }
    
    .glass-hero h1 {
        font-size: 3rem;
        margin: 0;
        color: var(--text);
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 50%, var(--accent-3) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    
    .auth-input-group {
        margin-bottom: 16px;
    }
    
    .auth-input {
        width: 100% !important;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid var(--border) !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .auth-input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
        background: rgba(124,58,237,0.05) !important;
    }
    
    .login-cta { 
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
        color: white;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(124,58,237,0.3);
    }
    
    .login-cta:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(124,58,237,0.4);
    }
    
    /* Sidebar styling */
    .nav-link-selected {
        background-color: rgba(124,58,237,0.2) !important;
        border-left: 3px solid var(--accent) !important;
        color: var(--accent) !important;
    }
    
    /* Page content */
    .page-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 8px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--text) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .page-subtitle {
        color: var(--muted);
        font-size: 1rem;
        margin-bottom: 24px;
    }
    
    /* Dividers */
    .stDivider {
        border-color: var(--border) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# ---------- DB / Auth Helpers ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT, email TEXT, created_date TEXT)''')
conn.commit()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str, email: str):
    try:
        created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO users VALUES (?,?,?,?)",
                  (username, hash_password(password), email, created_date))
        conn.commit()
        return True, "Account Created Successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)


def login_user(username: str, password: str) -> bool:
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone() is not None


def safe_rerun():
    """Call Streamlit rerun in a safe way that works across versions."""
    try:
        # preferred API if available (use getattr to avoid static attribute errors)
        rerun_fn = getattr(st, "experimental_rerun", None)
        if callable(rerun_fn):
            rerun_fn()
            return
    except Exception:
        # fallback: toggle a sentinel session key and stop to force a rerun on next interaction
        st.session_state.__needs_rerun = not st.session_state.get("__needs_rerun", False)
        try:
            st.stop()
        except Exception:
            pass

# ---------- Session init ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.login_time = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False
if "data" not in st.session_state:
    st.session_state.data = None

# ---------- Sidebar uploader (available before login) ----------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0;'>
        <div class='brand-badge'>🏥 MedIntel X</div>
        <div class='small-muted' style='margin-top:6px;'>Elite Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<div style='font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; color:var(--muted); margin:16px 0 12px 0;'>📤 Data Management</div>", unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📁 Upload CSV", type=["csv"], key="sidebar_upload", help="Upload healthcare data (max 200MB)")
    if uploaded is not None:
        try:
            st.session_state.data = pd.read_csv(uploaded)
            st.success("✅ Data uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

    if st.button("🔄 Load Backend Sample Data", use_container_width=True, help="Fetch sample data from backend API"):
        try:
            patients = requests.get("http://127.0.0.1:8000/patients", timeout=4).json()
            st.session_state.data = pd.DataFrame(patients)
            st.success("✅ Sample data loaded!")
        except Exception as e:
            st.error(f"❌ Backend error: {e}")

    st.divider()

# ---------- Elite Login / Register UI ----------
if not st.session_state.authenticated:
    # Hero section with gradient
    st.markdown("""
    <div class='glass-hero'>
        <h1>🏥 MedIntel X</h1>
        <div style='text-align:center; margin-top:16px;'>
            <div style='color:var(--text-secondary); font-size:1.1rem; font-weight:500;'>
                Premium Healthcare Intelligence Platform
            </div>
            <div style='color:var(--muted); font-size:0.95rem; margin-top:8px;'>
                Advanced Analytics & Real-Time Insights
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Auth form with three columns layout
    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    
    with col_center:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        if not st.session_state.show_register:
            # LOGIN FORM
            st.markdown("<div class='auth-title'>🔐 Sign In</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-subtitle'>Access your analytics dashboard</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", key="login_username", label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password", label_visibility="collapsed")
            
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            col_login, col_reg = st.columns(2, gap="medium")
            
            with col_login:
                if st.button("🔓 Sign In", use_container_width=True, key="login_btn"):
                    if username and password:
                        if login_user(username, password):
                            st.session_state.authenticated = True
                            st.session_state.user = username
                            st.session_state.login_time = datetime.datetime.now().isoformat()
                            st.success("✅ Welcome back! Redirecting...")
                            st.balloons()
                            safe_rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please enter both username and password")
            
            with col_reg:
                if st.button("📋 Register", use_container_width=True, key="reg_btn"):
                    st.session_state.show_register = True
                    safe_rerun()
            
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background:rgba(124,58,237,0.1); padding:14px; border-radius:12px; border:1px solid rgba(124,58,237,0.2);'>
                <div style='color:var(--text-secondary); font-size:0.9rem;'>
                    💡 <b>Demo Tip:</b><br>Upload CSV data in the sidebar or use backend sample data to explore the dashboard.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # REGISTER FORM
            st.markdown("<div class='auth-title'>📝 Create Account</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-subtitle'>Join MedIntel X platform</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            new_username = st.text_input("Username", placeholder="Choose a username", key="reg_username", label_visibility="collapsed")
            new_email = st.text_input("Email", placeholder="Your email address", key="reg_email", label_visibility="collapsed")
            new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="reg_password", label_visibility="collapsed")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm", label_visibility="collapsed")
            
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            col_create, col_back = st.columns(2, gap="medium")
            
            with col_create:
                if st.button("✅ Create Account", use_container_width=True, key="create_btn"):
                    if not new_username or not new_email or not new_password:
                        st.error("❌ All fields are required")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    else:
                        success, message = register_user(new_username, new_password, new_email)
                        if success:
                            st.success("✅ " + message)
                            st.info("📧 Now you can sign in with your credentials")
                            st.session_state.show_register = False
                            safe_rerun()
                        else:
                            st.error("❌ " + message)
            
            with col_back:
                if st.button("← Back", use_container_width=True, key="back_btn"):
                    st.session_state.show_register = False
                    safe_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align:center; padding:32px 0; color:var(--muted); font-size:0.85rem;'>
        <div>MedIntel X • Premium Healthcare Analytics</div>
        <div style='margin-top:4px; font-size:0.8rem;'>© 2026 • Secure • HIPAA Compliant</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------- Authenticated Sidebar & Navigation ----------
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:12px 0;'><div class=\'brand-badge\'>🏥 MedIntel X</div><div class=\'small-muted\'>Elite Dashboard</div></div>", unsafe_allow_html=True)
    st.divider()

    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Executive Center", "Patient Flow", "Financial Analysis", "Doctor Performance", "Forecasts", "Reports", "Profile"],
        icons=["house-fill", "bar-chart-fill", "shuffle", "wallet2", "stethoscope", "graph-up-arrow", "file-earmark-pdf", "person-circle"],
        default_index=1,
        styles={"container": {"padding": "0px", "background-color": "transparent"},
                "icon": {"color": "var(--accent)", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "text-align": "left"},
                "nav-link-selected": {"background-color": "rgba(124,58,237,0.16)", "color": "white"}}
    )

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<div style='padding:8px 10px; border-radius:10px; color:var(--muted);'>👤 <b>{st.session_state.user}</b><br><small>Administrator</small></div>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            safe_rerun()

# ---------- Page runner (executes scripts from pages/) ----------
PAGE_FILES = {
    "Executive Center": "1_Executive_Command_Center.py",
    "Patient Flow": "2_Patient_Flow_Sankey.py",
    "Financial Analysis": "3_Financial_Heatmap.py",
    "Doctor Performance": "4_Doctor_Performance_Radar.py",
    "Forecasts": "5_Forecast_Analytics.py",
    "Reports": "6_Reports.py",
    "Profile": "7_Profile.py",
}

base_pages_dir = os.path.join(os.path.dirname(__file__), "pages")

if selected == "Dashboard":
    st.markdown("<div class='page-title'>📊 Dashboard Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Real-time KPIs and business metrics</div>", unsafe_allow_html=True)

    df = st.session_state.data
    if df is None:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            <div class='card'>
                <div style='color:var(--muted); font-size:1.1rem; margin-bottom:16px;'>
                    📤 No Data Loaded
                </div>
                <div style='color:var(--text-secondary); font-size:0.95rem; line-height:1.6;'>
                    To view analytics and KPIs, please:
                    <div style='margin-top:12px; padding-left:12px;'>
                        • Upload a CSV file in the sidebar<br>
                        • Click "Use Backend Sample Data" button
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Calculate KPIs
        total_patients = len(df)
        total_revenue = df['treatment_cost'].sum() if 'treatment_cost' in df.columns else 0
        readmission_rate = (df['readmission'].astype(str) == 'Yes').mean() * 100 if 'readmission' in df.columns else 0
        
        # Additional KPIs
        avg_length_stay = df['length_of_stay'].mean() if 'length_of_stay' in df.columns else 0
        total_appointments = len(df)
        
        # Display KPI Cards in 2x2 grid
        row1_col1, row1_col2 = st.columns(2, gap="medium")
        row2_col1, row2_col2 = st.columns(2, gap="medium")
        
        with row1_col1:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>👥 Total Patients</div>
                <div class='metric-value'>{:,}</div>
                <div class='metric-subtitle'>Active records in system</div>
            </div>
            """.format(total_patients), unsafe_allow_html=True)
        
        with row1_col2:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>💰 Total Revenue</div>
                <div class='metric-value'>₹{:,.0f}</div>
                <div class='metric-subtitle'>Sum of all treatment costs</div>
            </div>
            """.format(total_revenue), unsafe_allow_html=True)
        
        with row2_col1:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>🔄 Readmission Rate</div>
                <div class='metric-value'>{:.1f}%</div>
                <div class='metric-subtitle'>Patient readmission percentage</div>
            </div>
            """.format(readmission_rate), unsafe_allow_html=True)
        
        with row2_col2:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>📅 Avg. Length of Stay</div>
                <div class='metric-value'>{:.1f} days</div>
                <div class='metric-subtitle'>Average patient stay duration</div>
            </div>
            """.format(avg_length_stay), unsafe_allow_html=True)
        
        # Data preview section
        st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.1rem; font-weight:600; color:var(--text); margin-bottom:12px;'>📋 Data Preview</div>", unsafe_allow_html=True)
        
        col_info, col_cols = st.columns([1, 2])
        with col_info:
            st.markdown(f"""
            <div class='card'>
                <div style='color:var(--muted); font-weight:600; margin-bottom:12px;'>Dataset Info</div>
                <div style='color:var(--text-secondary); font-size:0.95rem; line-height:2;'>
                    <b>Rows:</b> {len(df):,}<br>
                    <b>Columns:</b> {len(df.columns)}<br>
                    <b>Memory:</b> ~{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_cols:
            st.markdown("<div class='card'><b>Columns Available</b>: " + ", ".join([f"<code>{c}</code>" for c in df.columns[:8]]) + "</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        with st.expander("📊 View Full Dataset", expanded=False):
            st.dataframe(df, use_container_width=True, height=400)

else:
    # attempt to locate and run the corresponding page script
    filename = PAGE_FILES.get(selected)
    if filename:
        filepath = os.path.join(base_pages_dir, filename)
        if os.path.exists(filepath):
            try:
                # make uploaded/session data available to the page via a global variable
                globals_for_page = {"st": st, "pd": pd, "requests": requests, "session_data": st.session_state.get('data')}
                runpy.run_path(filepath, init_globals=globals_for_page, run_name="__main__")
            except Exception as e:
                st.error(f"Error running page {selected}: {e}")
        else:
            st.error(f"Page file not found: {filepath}")
    else:
        st.info("Page not implemented yet.")

# Footer
st.markdown("""
<div style='text-align:center; padding:32px 0; margin-top:40px; border-top:1px solid var(--border);'>
    <div style='color:var(--muted); font-size:0.9rem; font-weight:500;'>MedIntel X • Premium Healthcare Analytics Platform</div>
    <div style='color:var(--muted); font-size:0.8rem; margin-top:8px;'>© 2026 • Secure • HIPAA Compliant</div>
    <div style='color:var(--muted); font-size:0.75rem; margin-top:4px;'>Version 2.0 • Enhanced Dark Theme</div>
</div>
""", unsafe_allow_html=True)
