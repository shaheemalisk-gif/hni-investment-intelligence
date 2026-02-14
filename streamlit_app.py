"""
HNI Investment Intelligence Platform - Streamlit Web Interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="HNI Investment Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import project modules
try:
    from src.models.health_scorer import CompanyHealthScorer
    from src.models.portfolio_ranker import PortfolioRanker
    from src.utils.helpers import format_market_cap
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Some features may be limited in demo mode")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'health_scorer' not in st.session_state:
    try:
        st.session_state.health_scorer = CompanyHealthScorer()
    except:
        st.session_state.health_scorer = None

if 'portfolio_ranker' not in st.session_state:
    try:
        st.session_state.portfolio_ranker = PortfolioRanker()
    except:
        st.session_state.portfolio_ranker = None

# Load data
@st.cache_data
def load_data():
    """Load the main dataset"""
    try:
        return pd.read_csv('data/processed/stock_universe_engineered.csv')
    except FileNotFoundError:
        st.error("Data file not found. Please run data collection scripts.")
        return pd.DataFrame()

# Header
st.markdown('<p class="main-header">📈 HNI Investment Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown("### AI-Powered Stock Analysis & Portfolio Recommendations")

# Sidebar - Data Status Section
st.sidebar.title("🎯 Navigation")

# Add Data Architecture section
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Data Architecture")

# Show data status
data_file = 'data/processed/stock_universe_engineered.csv'

try:
    if os.path.exists(data_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(data_file))
        age = datetime.now() - file_time
        age_days = age.days
        age_hours = age.seconds // 3600
        
        # Status badge
        if age_days == 0 and age_hours < 6:
            badge = "🟢 Fresh"
            st.sidebar.success(f"{badge} | Updated: {file_time.strftime('%b %d, %I:%M %p')}")
        elif age_days < 7:
            badge = f"🟡 {age_days}d old"
            st.sidebar.warning(f"{badge} | Updated: {file_time.strftime('%b %d, %Y')}")
        else:
            badge = f"🔴 {age_days}d old"
            st.sidebar.error(f"{badge} | Updated: {file_time.strftime('%b %d, %Y')}")
    else:
        st.sidebar.error("❌ Data file not found")
except Exception as e:
    st.sidebar.error(f"Error checking data: {e}")

# Architecture explanation
with st.sidebar.expander("🏗️ Data Pipeline Architecture"):
    st.markdown("""
    **Demo Configuration:**
    - Source: Static CSV snapshot
    - Update: Manual (development)
    - Purpose: Algorithm validation
    
    **Production Configuration:**
    - Source: Bloomberg/Yahoo Finance API
    - Update: Scheduled (every 6 hours)
    - Cache: Redis (1-hour TTL)
    - Prices: Real-time during market hours
    
    **Modular Design:**
```python
    class DataSource:
        def fetch(): pass
    
    # Swap sources without code changes
    source = CSVSource()      # Demo
    source = LiveAPISource()  # Prod
```
    
    **Migration Time:** ~4 hours  
    **Breaking Changes:** None
    """)

# Page navigation
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Dashboard", "🏆 Portfolio Recommendations", "🏥 Company Health Checker", 
     "📊 Market Overview", "ℹ️ About"]
)

# Load data
df = load_data()

if df.empty:
    st.error("⚠️ No data available. Please check data files.")
    st.stop()

# Rest of your app code continues here...
# (Keep all your existing page logic)

def main():
    """Main application logic"""
    
    if page == "🏠 Dashboard":
        st.header("📊 Executive Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", len(df))
        with col2:
            st.metric("Avg Health Score", f"{df['composite_score'].mean():.1f}%")
        with col3:
            profitable = df['is_profitable'].sum()
            st.metric("Profitable", f"{profitable} ({profitable/len(df)*100:.0f}%)")
        with col4:
            high_quality = (df['quality_score'] > 70).sum()
            st.metric("High Quality", high_quality)
        
        st.markdown("---")
        
        # Add your dashboard content here...
        st.info("Dashboard content here...")
    
    elif page == "🏆 Portfolio Recommendations":
        st.header("🏆 Investment Portfolio Recommendations")
        st.info("Portfolio recommendations here...")
    
    elif page == "🏥 Company Health Checker":
        st.header("🏥 Company Health Analysis")
        st.info("Health checker here...")
    
    elif page == "📊 Market Overview":
        st.header("📊 Market Overview")
        st.info("Market overview here...")
    
    elif page == "ℹ️ About":
        st.header("ℹ️ About This Platform")
        st.markdown("""
        ## 🏆 HNI Investment Intelligence Platform
        
        **AI-Powered Stock Analysis & Portfolio Recommendations**
        
        ### Key Features:
        - Multi-dimensional health scoring
        - Portfolio recommendations across 4 market cap tiers
        - Statistical outlier detection
        - Interactive visualizations
        
        ### Technology:
        - Python 3.12 + Pandas + NumPy
        - Streamlit (Web UI)
        - Plotly (Interactive charts)
        - yfinance (Market data)
        
        ### Data:
        - 102 major US companies
        - 59 engineered features per company
        - 6-dimensional health analysis
        
        **Built for the HNI Investment Platform Assessment**
        """)

if __name__ == "__main__":
    main()
