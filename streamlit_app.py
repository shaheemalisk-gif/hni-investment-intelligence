"""
HNI Investment Intelligence Platform - Streamlit Web Interface
Interactive dashboard for portfolio recommendations and company health analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from src.models.health_scorer import CompanyHealthScorer
from src.models.portfolio_ranker import PortfolioRanker
from src.utils.helpers import format_market_cap

# Page configuration
st.set_page_config(
    page_title="HNI Investment Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.session_state.health_scorer = CompanyHealthScorer()
if 'portfolio_ranker' not in st.session_state:
    st.session_state.portfolio_ranker = PortfolioRanker()

# Load data
@st.cache_data
def load_data():
    """Load the main dataset"""
    return pd.read_csv('data/processed/stock_universe_engineered.csv')

@st.cache_data
def load_portfolio_results():
    """Load portfolio ranking results"""
    ranker = PortfolioRanker()
    return ranker.rank_all_categories()

def create_health_gauge(score, title="Health Score"):
    """Create a gauge chart for health score"""
    
    # Determine color based on score
    if score >= 70:
        color = "green"
    elif score >= 50:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24}},
        delta = {'reference': 50},
        gauge = {
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
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
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
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
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
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🏠 Dashboard", "🏆 Portfolio Recommendations", "🏥 Company Health Checker", "📊 Market Overview", "ℹ️ About"]
    )
    
    # Load data
    df = load_data()
    
    # PAGE 1: DASHBOARD
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
        
        # Quick stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Top 10 Overall Picks")
            top10 = df.nlargest(10, 'composite_score')[['symbol', 'company_name', 'composite_score', 'sector_category']]
            st.dataframe(
                top10.style.format({'composite_score': '{:.2f}'}),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.subheader("🎯 Score Distribution")
            fig = px.histogram(
                df, 
                x='composite_score', 
                nbins=20,
                title="Composite Score Distribution",
                labels={'composite_score': 'Composite Score', 'count': 'Number of Companies'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Sector breakdown
        st.subheader("🏢 Sector Performance")
        sector_stats = df.groupby('sector_category').agg({
            'composite_score': 'mean',
            'market_cap': 'sum',
            'symbol': 'count'
        }).round(2)
        sector_stats.columns = ['Avg Score', 'Total Market Cap', 'Count']
        sector_stats = sector_stats.sort_values('Avg Score', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                sector_stats.reset_index(),
                x='sector_category',
                y='Avg Score',
                title="Average Score by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(sector_stats, use_container_width=True)
    
    # PAGE 2: PORTFOLIO RECOMMENDATIONS
    elif page == "🏆 Portfolio Recommendations":
        st.header("🏆 Investment Portfolio Recommendations")
        
        st.info("📌 AI-powered rankings across 4 market cap categories with detailed analysis")
        
        # Load portfolio results
        with st.spinner("Generating portfolio recommendations..."):
            results = load_portfolio_results()
        
        # Category selector
        category = st.selectbox(
            "Select Category",
            ["Magnificent 7", "Giant Cap (>$500B)", "Large Cap ($100B-$500B)", "Mid Cap (<$100B)", "Overall Top 20"]
        )
        
        # Map selection to key
        category_map = {
            "Magnificent 7": "mag7",
            "Giant Cap (>$500B)": "giant",
            "Large Cap ($100B-$500B)": "large",
            "Mid Cap (<$100B)": "mid",
            "Overall Top 20": "overall_top20"
        }
        
        cat_key = category_map[category]
        cat_result = results[cat_key]
        
        # Display statistics
        st.subheader(f"📊 {category} - Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        stats = cat_result['statistics']
        
        with col1:
            st.metric("Total Companies", cat_result['total_companies'])
        with col2:
            st.metric("Avg Composite Score", f"{stats['avg_composite_score']:.2f}")
        with col3:
            st.metric("Total Market Cap", format_market_cap(stats['total_market_cap']))
        with col4:
            st.metric("Profitable", f"{stats['profitable_pct']:.0f}%")
        
        # Risk distribution
        st.subheader("⚠️ Risk Distribution")
        risk_data = pd.DataFrame({
            'Risk Level': ['Low Risk', 'Medium Risk', 'High Risk'],
            'Percentage': [stats['low_risk_pct'], stats['medium_risk_pct'], stats['high_risk_pct']]
        })
        
        fig = px.pie(risk_data, values='Percentage', names='Risk Level', 
                     color_discrete_sequence=['green', 'yellow', 'red'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Top picks chart
        st.subheader(f"🎯 Top {cat_result['top_n']} Recommendations")
        
        fig = create_portfolio_chart(cat_result['top_picks'], cat_result['top_n'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.subheader("📋 Detailed Rankings")
        
        display_df = cat_result['top_picks'][[
            'rank', 'symbol', 'company_name', 'rank_score', 
            'quality_score', 'value_score', 'growth_score', 
            'market_cap', 'risk_category'
        ]].copy()
        
        display_df['market_cap'] = display_df['market_cap'].apply(lambda x: format_market_cap(x))
        
        st.dataframe(
            display_df.style.format({
                'rank_score': '{:.2f}',
                'quality_score': '{:.2f}',
                'value_score': '{:.2f}',
                'growth_score': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Top 3 analysis
        st.subheader("🔍 Detailed Analysis - Top 3")
        
        for i, (_, row) in enumerate(cat_result['top_picks'].head(3).iterrows(), 1):
            with st.expander(f"#{i} - {row['symbol']} - {row['company_name']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rank Score", f"{row['rank_score']:.2f}")
                    st.metric("Market Cap", format_market_cap(row['market_cap']))
                
                with col2:
                    st.metric("P/E Ratio", f"{row.get('pe_ratio', 'N/A'):.2f}" if pd.notna(row.get('pe_ratio')) else "N/A")
                    st.metric("Profit Margin", f"{row['profit_margin']*100:.2f}%")
                
                with col3:
                    st.metric("Revenue Growth", f"{row['revenue_growth']*100:.2f}%")
                    st.metric("Risk", row['risk_category'])
                
                # Score breakdown
                score_data = pd.DataFrame({
                    'Dimension': ['Quality', 'Value', 'Growth', 'Momentum'],
                    'Score': [row['quality_score'], row['value_score'], 
                             row['growth_score'], row['momentum_score']]
                })
                
                fig = px.bar(score_data, x='Dimension', y='Score', 
                            title="Score Breakdown")
                st.plotly_chart(fig, use_container_width=True)
    
    # PAGE 3: COMPANY HEALTH CHECKER
    elif page == "🏥 Company Health Checker":
        st.header("🏥 Company Health Analysis")
        
        st.info("📌 Enter a stock symbol to get instant health analysis with AI-generated insights")
        
        # Symbol input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            symbol_input = st.text_input(
                "Enter Stock Symbol",
                placeholder="e.g., NVDA, AAPL, MSFT",
                help="Enter a ticker symbol from the analyzed universe"
            ).upper()
        
        with col2:
            analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
        
        # Available symbols
        with st.expander("📋 Available Symbols"):
            symbols_list = sorted(df['symbol'].unique())
            st.write(", ".join(symbols_list))
        
        # Perform analysis
        if analyze_button and symbol_input:
            with st.spinner(f"Analyzing {symbol_input}..."):
                scorer = st.session_state.health_scorer
                analysis = scorer.analyze_company(symbol_input)
            
            if 'error' in analysis:
                st.error(f"❌ {analysis['error']}")
            else:
                # Success - display results
                st.success(f"✅ Analysis complete for {analysis['company_name']}")
                
                # Overall health score
                st.subheader("🎯 Overall Health Assessment")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    fig = create_health_gauge(analysis['overall_health'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric("Risk Level", analysis['risk_level'])
                    st.metric("Sector", analysis['sector'].replace('_', ' ').title())
                
                with col3:
                    st.metric("Market Cap", format_market_cap(analysis['market_cap']))
                    
                    # Recommendation color coding
                    rec = analysis['recommendation']
                    if 'Buy' in rec or 'Strong' in rec:
                        st.markdown(f'<div class="success-box"><b>Recommendation:</b><br>{rec}</div>', unsafe_allow_html=True)
                    elif 'Hold' in rec:
                        st.markdown(f'<div class="warning-box"><b>Recommendation:</b><br>{rec}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="danger-box"><b>Recommendation:</b><br>{rec}</div>', unsafe_allow_html=True)
                
                # Dimension scores
                st.subheader("📊 Health Dimensions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Radar chart
                    fig = create_dimension_radar(analysis['dimension_scores'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Dimension table
                    dim_df = pd.DataFrame({
                        'Dimension': [k.replace('_', ' ').title() for k in analysis['dimension_scores'].keys()],
                        'Score': list(analysis['dimension_scores'].values())
                    })
                    
                    fig = px.bar(dim_df, x='Score', y='Dimension', orientation='h',
                                title="Dimension Scores")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Key metrics
                st.subheader("💰 Key Financial Metrics")
                
                metrics = analysis['key_metrics']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"${metrics['current_price']:.2f}")
                    if metrics['pe_ratio']:
                        st.metric("P/E Ratio", f"{metrics['pe_ratio']:.2f}")
                
                with col2:
                    st.metric("Profit Margin", f"{metrics['profit_margin']*100:.2f}%")
                    if metrics['roe']:
                        st.metric("ROE", f"{metrics['roe']*100:.2f}%")
                
                with col3:
                    st.metric("Revenue Growth", f"{metrics['revenue_growth']*100:.2f}%")
                    if metrics['beta']:
                        st.metric("Beta", f"{metrics['beta']:.2f}")
                
                with col4:
                    if metrics['debt_to_equity']:
                        st.metric("Debt/Equity", f"{metrics['debt_to_equity']:.2f}")
                    if metrics['dividend_yield']:
                        st.metric("Dividend Yield", f"{metrics['dividend_yield']*100:.2f}%")
                
                # Pros and Cons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Strengths (Pros)")
                    for pro in analysis['pros']:
                        st.markdown(f"- ✓ {pro}")
                
                with col2:
                    st.subheader("⚠️ Concerns (Cons)")
                    for con in analysis['cons']:
                        st.markdown(f"- ⚠ {con}")
    
    # PAGE 4: MARKET OVERVIEW
    elif page == "📊 Market Overview":
        st.header("📊 Market Overview")
        
        st.info("📌 Comprehensive view of the analyzed universe with interactive visualizations")
        
        # Filters
        st.subheader("🔍 Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sector_filter = st.multiselect(
                "Sector",
                options=sorted(df['sector_category'].unique()),
                default=None
            )
        
        with col2:
            risk_filter = st.multiselect(
                "Risk Level",
                options=['Low Risk', 'Medium Risk', 'High Risk'],
                default=None
            )
        
        with col3:
            profitability_filter = st.multiselect(
                "Profitability",
                options=sorted(df['profitability_status'].unique()),
                default=None
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if sector_filter:
            filtered_df = filtered_df[filtered_df['sector_category'].isin(sector_filter)]
        if risk_filter:
            filtered_df = filtered_df[filtered_df['risk_category'].isin(risk_filter)]
        if profitability_filter:
            filtered_df = filtered_df[filtered_df['profitability_status'].isin(profitability_filter)]
        
        st.write(f"**Showing {len(filtered_df)} companies**")
        
        # Scatter plot
        st.subheader("💹 Quality vs Value Analysis")
        
        fig = px.scatter(
            filtered_df,
            x='value_score',
            y='quality_score',
            size='market_cap',
            color='risk_category',
            hover_data=['symbol', 'company_name', 'composite_score'],
            title="Quality vs Value (bubble size = market cap)",
            labels={'value_score': 'Value Score', 'quality_score': 'Quality Score'},
            color_discrete_map={'Low Risk': 'green', 'Medium Risk': 'yellow', 'High Risk': 'red'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth vs Risk
        st.subheader("📈 Growth vs Risk Analysis")
        
        fig = px.scatter(
            filtered_df,
            x='risk_score',
            y='growth_score',
            size='market_cap',
            color='sector_category',
            hover_data=['symbol', 'company_name'],
            title="Growth Potential vs Risk Level",
            labels={'risk_score': 'Risk Score', 'growth_score': 'Growth Score'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Complete Dataset")
        
        display_cols = ['symbol', 'company_name', 'sector_category', 'market_cap',
                       'composite_score', 'quality_score', 'value_score', 'growth_score',
                       'risk_category', 'profitability_status']
        
        st.dataframe(
            filtered_df[display_cols].style.format({
                'market_cap': lambda x: format_market_cap(x),
                'composite_score': '{:.2f}',
                'quality_score': '{:.2f}',
                'value_score': '{:.2f}',
                'growth_score': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    # PAGE 5: ABOUT
    elif page == "ℹ️ About":
        st.header("ℹ️ About This Platform")
        
        st.markdown("""
        ## 🏆 HNI Investment Intelligence Platform
        
        **AI-Powered Stock Analysis & Portfolio Recommendations**
        
        ### 📋 Overview
        
        This platform provides comprehensive investment analysis for high-net-worth individuals,
        analyzing 102 major US companies across multiple dimensions to provide data-driven insights.
        
        ### ✨ Key Features
        
        #### 1. Portfolio Recommendations
        - **Magnificent 7**: Tech giants analysis
        - **Giant Cap**: Companies >$500B
        - **Large Cap**: Companies $100B-$500B
        - **Mid Cap**: Companies <$100B
        
        #### 2. Company Health Checker
        - 6-dimensional health analysis
        - AI-generated pros and cons
        - Risk assessment
        - Investment recommendations
        
        #### 3. Advanced Analytics
        - 59 engineered features per company
        - Composite scoring (Quality, Value, Growth, Momentum)
        - Altman Z-Score for bankruptcy prediction
        - Sector-relative performance metrics
        
        ### 🔧 Technology Stack
        
        - **Python 3.12**: Core language
        - **Streamlit**: Web interface
        - **Pandas**: Data manipulation
        - **Plotly**: Interactive visualizations
        - **yfinance**: Market data
        
        ### 📊 Data Coverage
        
        - **Companies**: 102 major US stocks
        - **Sectors**: 11 industry sectors
        - **Features**: 59 per company
        - **Update Frequency**: Daily (recommended)
        
        ### 🎯 Scoring Methodology
        
        **Health Score (0-100%)**:
        - Financial Strength (25%)
        - Profitability (20%)
        - Growth Trajectory (20%)
        - Valuation (15%)
        - Risk Management (10%)
        - Market Position (10%)
        
        **Ranking Score**:
        - Composite Score (30%)
        - Quality Score (20%)
        - Growth Score (20%)
        - Value Score (15%)
        - Momentum Score (15%)
        
        ### ⚠️ Disclaimer
        
        This tool is for **educational and informational purposes only**.
        - Not financial advice
        - Past performance ≠ future results
        - Always consult a licensed financial advisor
        - Conduct your own due diligence
        
        ### 📧 Contact
        
        Built by: [Your Name]  
        Date: February 2026  
        Purpose: HNI Investment Platform
        
        ---
        
        **Version**: 1.0.0  
        **Last Updated**: February 10, 2026
        """)

if __name__ == "__main__":
    main()
