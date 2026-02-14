"""
HNI Investment Intelligence Platform - Streamlit Web Interface
Interactive dashboard for portfolio recommendations and company health analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Page configuration - MUST BE FIRST STREAMLIT COMMAND!
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
    st.error(f"⚠️ Import error: {e}")
    CompanyHealthScorer = None
    PortfolioRanker = None
    format_market_cap = lambda x: f"${x/1e9:.2f}B"

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
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'health_scorer' not in st.session_state:
    if CompanyHealthScorer:
        try:
            st.session_state.health_scorer = CompanyHealthScorer()
        except:
            st.session_state.health_scorer = None
    else:
        st.session_state.health_scorer = None

if 'portfolio_ranker' not in st.session_state:
    if PortfolioRanker:
        try:
            st.session_state.portfolio_ranker = PortfolioRanker()
        except:
            st.session_state.portfolio_ranker = None
    else:
        st.session_state.portfolio_ranker = None

# Load data
@st.cache_data
def load_data():
    """Load the main dataset"""
    try:
        return pd.read_csv('data/processed/stock_universe_engineered.csv')
    except FileNotFoundError:
        st.error("Data file not found. Please check data/processed/ directory.")
        return pd.DataFrame()

@st.cache_data
def load_portfolio_results():
    """Load portfolio ranking results"""
    if PortfolioRanker:
        ranker = PortfolioRanker()
        return ranker.rank_all_categories()
    return {}

# Visualization functions
def create_health_gauge(score, title="Health Score"):
    """Create a gauge chart for health score"""
    color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 70], 'color': '#ffffcc'},
                {'range': [70, 100], 'color': '#ccffcc'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_dimension_radar(dimensions):
    """Create radar chart for health dimensions"""
    categories = list(dimensions.keys())
    values = list(dimensions.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Health Dimensions'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=400
    )
    return fig

def create_portfolio_chart(df, top_n=10):
    """Create bar chart for top picks"""
    top_picks = df.head(top_n)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_picks['symbol'],
        y=top_picks['rank_score'],
        text=top_picks['rank_score'].round(2),
        textposition='auto',
        marker_color='#1f77b4',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>'
    ))
    fig.update_layout(
        title=f"Top {top_n} Investment Picks",
        xaxis_title="Company",
        yaxis_title="Rank Score",
        height=400,
        showlegend=False
    )
    return fig

def main():
    """Main application"""
    
    # Header
    st.markdown('<p class="main-header">📈 HNI Investment Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Stock Analysis & Portfolio Recommendations")
    
    # Sidebar
    st.sidebar.title("🎯 Navigation")
    
    # Data Status Section
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Data Status")
    
    data_file = 'data/processed/stock_universe_engineered.csv'
    
    try:
        if os.path.exists(data_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(data_file))
            age = datetime.now() - file_time
            age_days = age.days
            age_hours = age.seconds // 3600
            
            if age_days == 0 and age_hours < 6:
                st.sidebar.success(f"🟢 Fresh | {file_time.strftime('%b %d, %I:%M %p')}")
            elif age_days < 7:
                st.sidebar.warning(f"🟡 {age_days}d old | {file_time.strftime('%b %d')}")
            else:
                st.sidebar.error(f"🔴 {age_days}d old | {file_time.strftime('%b %d')}")
        else:
            st.sidebar.error("❌ Data file not found")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
    
    # Architecture info
    with st.sidebar.expander("🏗️ Data Architecture"):
        st.markdown("""
        **Current:** Static snapshot  
        **Production:** Live API refresh
        
        **Implementation:**
        - Fundamentals: Daily refresh
        - Prices: 15-min updates
        - Modular data source design
        
        **Time to deploy:** ~4 hours
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
    
    # PAGE ROUTING
    if page == "🏠 Dashboard":
        show_dashboard(df)
    elif page == "🏆 Portfolio Recommendations":
        show_portfolio(df)
    elif page == "🏥 Company Health Checker":
        show_health_checker(df)
    elif page == "📊 Market Overview":
        show_market_overview(df)
    elif page == "ℹ️ About":
        show_about()

def show_dashboard(df):
    """Dashboard page"""
    st.header("📊 Executive Dashboard")
    
    # Metrics
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
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top 10 Overall Picks")
        top10 = df.nlargest(10, 'composite_score')[['symbol', 'company_name', 'composite_score', 'sector_category']]
        st.dataframe(top10, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🎯 Score Distribution")
        fig = px.histogram(df, x='composite_score', nbins=20, title="Composite Score Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_portfolio(df):
    """Portfolio recommendations page"""
    st.header("🏆 Portfolio Recommendations")
    st.info("AI-powered rankings across market cap categories")
    
    # Add your portfolio logic here
    st.write("Portfolio page - Add rankings table")

def show_health_checker(df):
    """Health checker page"""
    st.header("🏥 Company Health Checker")
    
    symbol_input = st.text_input("Enter Stock Symbol", placeholder="e.g., NVDA, AAPL").upper()
    
    if st.button("🔍 Analyze") and symbol_input:
        if st.session_state.health_scorer:
            with st.spinner(f"Analyzing {symbol_input}..."):
                analysis = st.session_state.health_scorer.analyze_company(symbol_input)
            
            if 'error' not in analysis:
                st.success(f"✅ Analysis complete for {analysis['company_name']}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = create_health_gauge(analysis['overall_health'])
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.metric("Risk Level", analysis['risk_level'])
                    st.metric("Recommendation", analysis['recommendation'])
            else:
                st.error(analysis['error'])
        else:
            st.error("Health scorer not available")

def show_market_overview(df):
    """Market overview page"""
    st.header("📊 Market Overview")
    
    fig = px.scatter(
        df,
        x='value_score',
        y='quality_score',
        size='market_cap',
        color='risk_category',
        hover_data=['symbol', 'company_name'],
        title="Quality vs Value Analysis"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_about():
    """About page"""
    st.header("ℹ️ About This Platform")
    st.markdown("""
    ## 🏆 HNI Investment Intelligence Platform
    
    **AI-Powered Stock Analysis & Portfolio Recommendations**
    
    ### Features:
    - 102 companies analyzed
    - 59 engineered features
    - 6-dimensional health scoring
    - Interactive visualizations
    
    ### Technology:
    - Python 3.12 + Pandas + NumPy
    - Streamlit + Plotly
    - Statistical modeling (not ML)
    
    **Built by:** Muhammed Shaheem OP  
    **Date:** February 2026
    """)

if __name__ == "__main__":
    main()
