"""
Company Health Scoring System
Analyzes company health from multiple dimensions and generates pros/cons
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import logger
from src.utils.helpers import format_market_cap

class CompanyHealthScorer:
    """
    Comprehensive company health analysis
    Generates health score (0-100%) and detailed pros/cons
    """
    
    def __init__(self, data_path: str = 'data/processed/stock_universe_engineered.csv'):
        """Initialize with engineered dataset"""
        self.df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(self.df)} companies for health analysis")
        
        # Define weight for each health dimension
        self.weights = {
            'financial_strength': 0.25,
            'profitability': 0.20,
            'growth_trajectory': 0.20,
            'valuation': 0.15,
            'risk_management': 0.10,
            'market_position': 0.10
        }
    
    def analyze_company(self, symbol: str) -> dict:
        """
        Complete health analysis for a company
        
        Returns:
            dict with keys: overall_health, dimension_scores, pros, cons, 
                           risk_level, recommendation
        """
        
        symbol = symbol.upper()
        
        # Get company data
        company_data = self.df[self.df['symbol'] == symbol]
        
        if company_data.empty:
            return {
                'error': f"Symbol {symbol} not found in database",
                'available_symbols': self.df['symbol'].tolist()[:20]
            }
        
        company = company_data.iloc[0]
        
        logger.info(f"Analyzing health for {symbol} - {company['company_name']}")
        
        # Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(company)
        
        # Calculate overall health
        overall_health = self._calculate_overall_health(dimension_scores)
        
        # Generate pros and cons
        pros, cons = self._generate_pros_cons(company, dimension_scores)
        
        # Determine risk level and recommendation
        risk_level = self._assess_risk_level(company)
        recommendation = self._generate_recommendation(overall_health, risk_level, company)
        
        result = {
            'symbol': symbol,
            'company_name': company['company_name'],
            'overall_health': round(overall_health, 2),
            'dimension_scores': dimension_scores,
            'pros': pros,
            'cons': cons,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'key_metrics': self._extract_key_metrics(company),
            'sector': company['sector_category'],
            'market_cap': company['market_cap']
        }
        
        return result
    
    def _calculate_dimension_scores(self, company: pd.Series) -> dict:
        """Calculate scores for each health dimension"""
        
        scores = {}
        
        # 1. Financial Strength (Debt, Cash Flow, Liquidity)
        debt_score = self._score_debt_level(company)
        cash_score = self._score_cash_flow(company)
        liquidity_score = self._score_liquidity(company)
        scores['financial_strength'] = np.nanmean([debt_score, cash_score, liquidity_score])
        
        # 2. Profitability (Margins, ROE, ROA)
        margin_score = min(100, company.get('profit_margin', 0) * 500)  # Scale up
        roe_score = min(100, company.get('roe', 0) * 500)
        quality_score = company.get('quality_score', 50)
        scores['profitability'] = np.nanmean([margin_score, roe_score, quality_score])
        
        # 3. Growth Trajectory
        scores['growth_trajectory'] = company.get('growth_score', 50)
        
        # 4. Valuation (Is it reasonably priced?)
        scores['valuation'] = company.get('value_score', 50)
        
        # 5. Risk Management
        risk_score = 100 - (company.get('risk_score', 5) * 10)  # Invert risk score
        beta_score = max(0, 100 - abs(company.get('beta', 1) - 1) * 50)
        scores['risk_management'] = np.nanmean([risk_score, beta_score])
        
        # 6. Market Position (Size, Momentum)
        market_cap = company.get('market_cap', 0)
        size_score = min(100, np.log10(market_cap) * 10) if market_cap > 0 else 0
        momentum_score = company.get('momentum_score', 50)
        scores['market_position'] = np.nanmean([size_score, momentum_score])
        
        # Round all scores
        scores = {k: round(v, 2) for k, v in scores.items()}
        
        return scores
    
    def _score_debt_level(self, company: pd.Series) -> float:
        """Score based on debt levels (lower debt = better)"""
        debt_to_equity = company.get('debt_to_equity', 0.5)
        
        if pd.isna(debt_to_equity):
            return 50  # Neutral
        
        # Scoring: <0.3 = excellent, 0.3-0.7 = good, 0.7-1.5 = fair, >1.5 = poor
        if debt_to_equity < 0.3:
            return 100
        elif debt_to_equity < 0.7:
            return 80
        elif debt_to_equity < 1.5:
            return 60
        else:
            return max(0, 60 - (debt_to_equity - 1.5) * 20)
    
    def _score_cash_flow(self, company: pd.Series) -> float:
        """Score based on free cash flow"""
        fcf = company.get('free_cash_flow', 0)
        
        if pd.isna(fcf) or fcf == 0:
            return 50  # Neutral if missing
        
        # Positive FCF is good
        if fcf > 0:
            # Score based on FCF as % of market cap
            fcf_yield = (fcf / company.get('market_cap', 1)) * 100
            return min(100, 50 + fcf_yield * 10)
        else:
            return 30  # Negative FCF is concerning
    
    def _score_liquidity(self, company: pd.Series) -> float:
        """Score based on current ratio"""
        current_ratio = company.get('current_ratio', 1.5)
        
        if pd.isna(current_ratio):
            return 50
        
        # Current ratio > 1.5 is good, > 2.0 is excellent
        if current_ratio > 2.5:
            return 100
        elif current_ratio > 2.0:
            return 90
        elif current_ratio > 1.5:
            return 75
        elif current_ratio > 1.0:
            return 60
        else:
            return 40
    
    def _calculate_overall_health(self, dimension_scores: dict) -> float:
        """Calculate weighted overall health score"""
        
        overall = sum(
            dimension_scores.get(dimension, 50) * weight
            for dimension, weight in self.weights.items()
        )
        
        return min(100, max(0, overall))
    
    def _generate_pros_cons(self, company: pd.Series, dimension_scores: dict) -> tuple:
        """Generate detailed pros and cons"""
        
        pros = []
        cons = []
        
        # Financial Strength
        if dimension_scores['financial_strength'] > 70:
            debt = company.get('debt_to_equity', 0)
            pros.append(f"Strong financial position with low debt (D/E: {debt:.2f})")
        elif dimension_scores['financial_strength'] < 40:
            debt = company.get('debt_to_equity', 0)
            cons.append(f"High debt levels may pose risk (D/E: {debt:.2f})")
        
        # Profitability
        profit_margin = company.get('profit_margin', 0)
        if profit_margin > 0.20:
            pros.append(f"Exceptional profit margins ({profit_margin*100:.1f}%)")
        elif profit_margin > 0.10:
            pros.append(f"Healthy profit margins ({profit_margin*100:.1f}%)")
        elif profit_margin < 0:
            cons.append(f"Company is currently unprofitable (margin: {profit_margin*100:.1f}%)")
        elif profit_margin < 0.05:
            cons.append(f"Thin profit margins ({profit_margin*100:.1f}%)")
        
        # ROE
        roe = company.get('roe', 0)
        if roe > 0.20:
            pros.append(f"Strong return on equity (ROE: {roe*100:.1f}%)")
        elif roe < 0:
            cons.append("Negative return on equity")
        
        # Growth
        revenue_growth = company.get('revenue_growth', 0)
        if revenue_growth > 0.15:
            pros.append(f"Impressive revenue growth ({revenue_growth*100:.1f}% YoY)")
        elif revenue_growth > 0.08:
            pros.append(f"Solid revenue growth ({revenue_growth*100:.1f}% YoY)")
        elif revenue_growth < 0:
            cons.append(f"Declining revenues ({revenue_growth*100:.1f}% YoY)")
        elif revenue_growth < 0.03:
            cons.append(f"Slow revenue growth ({revenue_growth*100:.1f}% YoY)")
        
        # Valuation
        pe_ratio = company.get('pe_ratio', 0)
        if pd.notna(pe_ratio):
            if pe_ratio < 15:
                pros.append(f"Attractively valued (P/E: {pe_ratio:.1f})")
            elif pe_ratio > 40:
                cons.append(f"High valuation multiple (P/E: {pe_ratio:.1f})")
        
        peg_ratio = company.get('peg_ratio', 0)
        if pd.notna(peg_ratio) and peg_ratio > 0:
            if peg_ratio < 1.0:
                pros.append(f"Growth at reasonable price (PEG: {peg_ratio:.2f})")
            elif peg_ratio > 2.0:
                cons.append(f"Expensive relative to growth (PEG: {peg_ratio:.2f})")
        
        # Risk factors
        beta = company.get('beta', 1)
        if beta < 0.8:
            pros.append(f"Lower volatility than market (Beta: {beta:.2f})")
        elif beta > 1.5:
            cons.append(f"Higher volatility than market (Beta: {beta:.2f})")
        
        # Cash flow
        fcf = company.get('free_cash_flow', 0)
        if pd.notna(fcf) and fcf > 0:
            fcf_billions = fcf / 1e9
            pros.append(f"Generates strong free cash flow (${fcf_billions:.2f}B)")
        elif pd.notna(fcf) and fcf < 0:
            cons.append("Negative free cash flow")
        
        # Market position
        market_cap = company.get('market_cap', 0)
        if market_cap > 100e9:
            pros.append(f"Large, established company ({format_market_cap(market_cap)})")
        
        # Momentum
        return_1y = company.get('return_1y', 0)
        if pd.notna(return_1y):
            if return_1y > 30:
                pros.append(f"Strong 1-year performance (+{return_1y:.1f}%)")
            elif return_1y < -20:
                cons.append(f"Poor 1-year performance ({return_1y:.1f}%)")
        
        # Dividend
        div_yield = company.get('dividend_yield', 0)
        if pd.notna(div_yield) and div_yield > 0.02:
            pros.append(f"Pays dividend (Yield: {div_yield*100:.2f}%)")
        
        # Sector-specific insights
        sector = company.get('sector_category', '')
        if sector == 'tech' and revenue_growth > 0.15:
            pros.append("Strong growth in tech sector")
        
        # Financial health (Altman Z-Score)
        z_score = company.get('altman_z_score', 0)
        if z_score > 3.0:
            pros.append("Low bankruptcy risk (Altman Z-Score)")
        elif z_score < 1.8:
            cons.append("Higher financial distress risk (Altman Z-Score)")
        
        # Ensure we have at least some pros and cons
        if not pros:
            pros.append("Company has stable operations")
        
        if not cons:
            cons.append("Monitor industry competition")
        
        return pros, cons
    
    def _assess_risk_level(self, company: pd.Series) -> str:
        """Determine overall risk level"""
        
        risk_category = company.get('risk_category', 'Medium Risk')
        financial_health = company.get('financial_health', 'Medium Risk')
        is_profitable = company.get('is_profitable', True)
        
        # Combine signals
        risk_signals = []
        
        if risk_category == 'High Risk':
            risk_signals.append('high')
        elif risk_category == 'Low Risk':
            risk_signals.append('low')
        
        if financial_health == 'High Risk':
            risk_signals.append('high')
        elif financial_health == 'Low Risk':
            risk_signals.append('low')
        
        if not is_profitable:
            risk_signals.append('high')
        
        # Determine overall
        high_count = risk_signals.count('high')
        low_count = risk_signals.count('low')
        
        if high_count >= 2:
            return "High Risk"
        elif low_count >= 2:
            return "Low Risk"
        else:
            return "Medium Risk"
    
    def _generate_recommendation(self, health_score: float, risk_level: str, 
                                 company: pd.Series) -> str:
        """Generate investment recommendation"""
        
        # Simple recommendation logic
        if health_score >= 70 and risk_level == "Low Risk":
            return "Strong Buy - Excellent health with low risk"
        elif health_score >= 70:
            return "Buy - Strong fundamentals, monitor risk factors"
        elif health_score >= 60 and risk_level != "High Risk":
            return "Buy - Good fundamentals, suitable for growth portfolios"
        elif health_score >= 50 and risk_level == "Low Risk":
            return "Hold - Stable but limited upside potential"
        elif health_score >= 50:
            return "Hold - Mixed signals, suitable for risk-tolerant investors"
        elif health_score >= 40:
            return "Hold/Sell - Significant concerns, review risk tolerance"
        else:
            return "Sell - Poor fundamentals, high risk"
    
    def _extract_key_metrics(self, company: pd.Series) -> dict:
        """Extract key metrics for display"""
        
        return {
            'current_price': company.get('current_price', 0),
            'market_cap': company.get('market_cap', 0),
            'pe_ratio': company.get('pe_ratio', None),
            'profit_margin': company.get('profit_margin', 0),
            'revenue_growth': company.get('revenue_growth', 0),
            'debt_to_equity': company.get('debt_to_equity', None),
            'roe': company.get('roe', None),
            'beta': company.get('beta', None),
            'dividend_yield': company.get('dividend_yield', None)
        }
    
    def format_analysis(self, analysis: dict) -> str:
        """Format analysis results as readable text"""
        
        if 'error' in analysis:
            return f"Error: {analysis['error']}"
        
        output = []
        output.append("="*80)
        output.append(f"COMPANY HEALTH ANALYSIS: {analysis['company_name']} ({analysis['symbol']})")
        output.append("="*80)
        output.append("")
        
        # Overall Health
        health = analysis['overall_health']
        output.append(f"Overall Health Score: {health:.1f}% - {self._health_rating(health)}")
        output.append(f"Risk Level: {analysis['risk_level']}")
        output.append(f"Recommendation: {analysis['recommendation']}")
        output.append("")
        
        # Dimension Scores
        output.append("-"*80)
        output.append("HEALTH DIMENSIONS:")
        output.append("-"*80)
        for dimension, score in analysis['dimension_scores'].items():
            bar = self._create_bar(score)
            output.append(f"{dimension.replace('_', ' ').title():25s}: {score:5.1f}% {bar}")
        output.append("")
        
        # Key Metrics
        output.append("-"*80)
        output.append("KEY METRICS:")
        output.append("-"*80)
        metrics = analysis['key_metrics']
        output.append(f"Market Cap: {format_market_cap(metrics['market_cap'])}")
        output.append(f"Current Price: ${metrics['current_price']:.2f}")
        if metrics['pe_ratio']:
            output.append(f"P/E Ratio: {metrics['pe_ratio']:.2f}")
        output.append(f"Profit Margin: {metrics['profit_margin']*100:.2f}%")
        output.append(f"Revenue Growth: {metrics['revenue_growth']*100:.2f}%")
        if metrics['debt_to_equity']:
            output.append(f"Debt/Equity: {metrics['debt_to_equity']:.2f}")
        if metrics['roe']:
            output.append(f"ROE: {metrics['roe']*100:.2f}%")
        if metrics['beta']:
            output.append(f"Beta: {metrics['beta']:.2f}")
        output.append("")
        
        # Pros
        output.append("-"*80)
        output.append("STRENGTHS (PROS):")
        output.append("-"*80)
        for i, pro in enumerate(analysis['pros'], 1):
            output.append(f"  ✓ {pro}")
        output.append("")
        
        # Cons
        output.append("-"*80)
        output.append("CONCERNS (CONS):")
        output.append("-"*80)
        for i, con in enumerate(analysis['cons'], 1):
            output.append(f"  ⚠ {con}")
        output.append("")
        
        output.append("="*80)
        
        return "\n".join(output)
    
    def _health_rating(self, score: float) -> str:
        """Convert numeric score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 40:
            return "Below Average"
        else:
            return "Poor"
    
    def _create_bar(self, score: float, width: int = 20) -> str:
        """Create visual bar for score"""
        filled = int((score / 100) * width)
        return "█" * filled + "░" * (width - filled)

# Global instance
health_scorer = CompanyHealthScorer()