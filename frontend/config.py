"""
MedIntel X - Configuration Settings
"""

# Application Settings
APP_NAME = "MedIntel X"
APP_VERSION = "2.0 Premium Edition"
APP_THEME = "Premium Healthcare Dashboard"

# UI Settings
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"
SUCCESS_COLOR = "#10B981"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"
LIGHT_BG = "#F9FAFB"
DARK_BG = "#1F2937"

# API Settings
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINTS = {
    "patients": "/patients",
    "departments": "/departments",
    "doctors": "/doctors",
    "admissions": "/admissions",
}

# Database Settings
DB_NAME = "users.db"
DB_TABLE = "users"
DB_TIMEOUT = 5

# Security Settings
PASSWORD_MIN_LENGTH = 6
PASSWORD_HASH_ALGORITHM = "sha256"
SESSION_TIMEOUT = 3600  # 1 hour in seconds
MAX_LOGIN_ATTEMPTS = 5

# Features Enabled
FEATURES = {
    "authentication": True,
    "registration": True,
    "session_management": True,
    "password_hashing": True,
    "data_export": True,
    "advanced_analytics": True,
    "forecasting": True,
}

# Page Configuration
PAGES = {
    "Dashboard": "📊",
    "Executive Center": "📊",
    "Patient Flow": "🔄",
    "Financial Analysis": "💰",
    "Doctor Performance": "🩺",
    "Forecasts": "📈",
    "Reports": "📄",
    "Profile": "👤",
}

# Color Palette
COLORS = {
    "primary": ["#667eea", "#764ba2", "#FF6B6B", "#10B981", "#F59E0B", "#8B5CF6"],
    "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "heatmap": "RdYlGn_r",
}

# Performance Settings
CACHE_TTL = 3600  # Cache time to live in seconds
MAX_ROWS_DISPLAY = 1000
CHART_HEIGHT = 400
CHART_WIDTH = "100%"

# Data Processing
DATA_AGGREGATION = {
    "department_stats": True,
    "age_groups": True,
    "revenue_analysis": True,
    "trend_analysis": True,
}

# Visualization Defaults
VISUALIZATION_DEFAULTS = {
    "hovermode": "x unified",
    "showlegend": True,
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "white",
}

# API KEYS (Store securely in environment variables)
# API_KEY = os.getenv("MEDINTEL_API_KEY")
# DATABASE_URL = os.getenv("DATABASE_URL")

# Feature Flags
DEBUG_MODE = False
LOG_LEVEL = "INFO"
ENABLE_PROFILING = False
ENABLE_ERROR_TRACKING = True

# Forecast Settings
FORECAST_DAYS = 30
FORECAST_CONFIDENCE = 95
ML_MODEL = "ARIMA"  # or "Prophet", "LSTM", etc.

# Notification Settings
NOTIFICATIONS = {
    "email": True,
    "sms": False,
    "push": True,
}

# Export Formats
EXPORT_FORMATS = [
    "CSV",
    "Excel",
    "PDF",
    "JSON",
]

# Audit Logging
AUDIT_LOG = {
    "enabled": True,
    "log_file": "audit.log",
    "log_level": "INFO",
}
