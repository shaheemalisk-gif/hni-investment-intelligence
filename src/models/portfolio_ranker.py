"""
Investment Portfolio Ranking System
Ranks companies within categories and generates top recommendations
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import logger
from src.utils.helpers import format_market_cap

class PortfolioRanker:
    """
    Intelligent ranking system for investment recommendations
    Ranks companies within market cap categories
    """
    
    def __init__(self, data_path: str = 'data/processed/stock_universe_engineered.csv'):
        """Initialize with engineered dataset"""
        self.df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(self.df)} companies for ranking")
        
        # Ranking weights - adjust for different investment styles
        self.weights = {
            'composite_score': 0.30,      # Overall quality
            'quality_score': 0.20,        # Business fundamentals
            'value_score': 0.15,          # Valuation attractiveness
            'growth_score': 0.20,         # Growth potential
            'momentum_score': 0.15        # Recent performance
        }
    
    def rank_all_categories(self) -> dict:
        """
        Rank companies in all categories
        
        Returns:
            dict with category rankings and top picks
        """
        
        results = {}
        
        logger.info("Starting portfolio ranking across all categories...")
        
        # 1. Magnificent 7 - Rank all 7
        results['mag7'] = self._rank_category('mag7', top_n=7, 
                                              description="Magnificent 7 Tech Giants")
        
        # 2. Giants - Top 5
        results['giant'] = self._rank_category('giant', top_n=5,
                                               description="Giant Companies (>$500B)")
        
        # 3. Large - Top 7
        results['large'] = self._rank_category('large', top_n=7,
                                               description="Large Cap ($100B-$500B)")
        
        # 4. Mid - Top 10
        results['mid'] = self._rank_category('mid', top_n=10,
                                             description="Mid Cap (<$100B)")
        
        # 5. Overall Top 20 across all companies
        results['overall_top20'] = self._get_overall_top_picks(top_n=20)
        
        logger.info("Portfolio ranking complete!")
        
        return results
    
    def _rank_category(self, category: str, top_n: int, description: str) -> dict:
        """
        Rank companies within a specific category
        
        Args:
            category: Category name (mag7, giant, large, mid)
            top_n: Number of top picks to return
            description: Category description
            
        Returns:
            dict with rankings and analysis
        """
        
        logger.info(f"Ranking {category} category...")
        
        # Load fresh category data with all engineered features
        cat_df = pd.read_csv(f'data/processed/category_{category}.csv')
        
        # Verify we have the required columns
        required_cols = ['composite_score', 'quality_score', 'value_score', 'growth_score', 'momentum_score']
        missing_cols = [col for col in required_cols if col not in cat_df.columns]
        
        if missing_cols:
            logger.error(f"Missing columns in {category}: {missing_cols}")
            raise ValueError(f"Category file missing required columns: {missing_cols}")
        
        # Calculate final ranking score
        cat_df['rank_score'] = (
            self.weights['composite_score'] * cat_df['composite_score'] +
            self.weights['quality_score'] * cat_df['quality_score'] +
            self.weights['value_score'] * cat_df['value_score'] +
            self.weights['growth_score'] * cat_df['growth_score'] +
            self.weights['momentum_score'] * cat_df['momentum_score']
        )
        
        # Sort by rank score
        cat_df = cat_df.sort_values('rank_score', ascending=False)
        cat_df['rank'] = range(1, len(cat_df) + 1)
        
        # Get top picks
        top_picks = cat_df.head(top_n)
        
        result = {
            'category': category,
            'description': description,
            'total_companies': len(cat_df),
            'top_n': top_n,
            'rankings': cat_df,
            'top_picks': top_picks,
            'statistics': self._calculate_category_stats(cat_df)
        }
        
        return result
    
    def _get_overall_top_picks(self, top_n: int = 20) -> dict:
        """Get top picks across all categories"""
        
        logger.info(f"Selecting overall top {top_n} picks...")
        
        df = self.df.copy()
        
        # Calculate ranking score
        df['rank_score'] = (
            self.weights['composite_score'] * df['composite_score'] +
            self.weights['quality_score'] * df['quality_score'] +
            self.weights['value_score'] * df['value_score'] +
            self.weights['growth_score'] * df['growth_score'] +
            self.weights['momentum_score'] * df['momentum_score']
        )
        
        # Sort and rank
        df = df.sort_values('rank_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        top_picks = df.head(top_n)
        
        result = {
            'category': 'overall',
            'description': 'Top Picks Across All Categories',
            'total_companies': len(df),
            'top_n': top_n,
            'rankings': df,
            'top_picks': top_picks,
            'statistics': self._calculate_category_stats(df)
        }
        
        return result
    
    def _calculate_category_stats(self, df: pd.DataFrame) -> dict:
        """Calculate statistics for a category"""
        
        stats = {
            'avg_composite_score': df['composite_score'].mean(),
            'avg_quality_score': df['quality_score'].mean(),
            'avg_value_score': df['value_score'].mean(),
            'avg_growth_score': df['growth_score'].mean(),
            'avg_market_cap': df['market_cap'].mean(),
            'total_market_cap': df['market_cap'].sum(),
            'profitable_pct': (df['profitability_status'].isin(['Profitable', 'Highly Profitable', 'Marginally Profitable']).sum() / len(df)) * 100,
            'low_risk_pct': (df['risk_category'] == 'Low Risk').sum() / len(df) * 100,
            'medium_risk_pct': (df['risk_category'] == 'Medium Risk').sum() / len(df) * 100,
            'high_risk_pct': (df['risk_category'] == 'High Risk').sum() / len(df) * 100
        }
        
        return stats
    
    def format_category_report(self, category_result: dict) -> str:
        """Format a category ranking as readable text"""
        
        output = []
        
        output.append("=" * 100)
        output.append(f"{category_result['description'].upper()}")
        output.append("=" * 100)
        output.append("")
        
        # Statistics
        stats = category_result['statistics']
        output.append(f"Total Companies: {category_result['total_companies']}")
        output.append(f"Top Picks Selected: {category_result['top_n']}")
        output.append(f"Average Composite Score: {stats['avg_composite_score']:.2f}")
        output.append(f"Total Market Cap: {format_market_cap(stats['total_market_cap'])}")
        output.append(f"Profitable Companies: {stats['profitable_pct']:.1f}%")
        output.append("")
        
        # Risk distribution
        output.append("Risk Distribution:")
        output.append(f"  Low Risk:    {stats['low_risk_pct']:5.1f}%")
        output.append(f"  Medium Risk: {stats['medium_risk_pct']:5.1f}%")
        output.append(f"  High Risk:   {stats['high_risk_pct']:5.1f}%")
        output.append("")
        
        # Top picks table
        output.append("-" * 100)
        output.append("TOP PICKS:")
        output.append("-" * 100)
        output.append("")
        
        # Header
        header = f"{'Rank':<6}{'Symbol':<8}{'Company':<35}{'Score':<8}{'Quality':<9}{'Value':<8}{'Growth':<8}{'Risk':<12}"
        output.append(header)
        output.append("-" * 100)
        
        # Rows
        for _, row in category_result['top_picks'].iterrows():
            company_name = row['company_name'][:33]
            line = (
                f"{int(row['rank']):<6}"
                f"{row['symbol']:<8}"
                f"{company_name:<35}"
                f"{row['rank_score']:.2f}    "
                f"{row['quality_score']:.2f}     "
                f"{row['value_score']:.2f}    "
                f"{row['growth_score']:.2f}    "
                f"{row['risk_category']:<12}"
            )
            output.append(line)
        
        output.append("")
        output.append("-" * 100)
        output.append("DETAILED ANALYSIS OF TOP 3:")
        output.append("-" * 100)
        output.append("")
        
        # Detailed analysis of top 3
        for i, (_, row) in enumerate(category_result['top_picks'].head(3).iterrows(), 1):
            output.append(f"{i}. {row['symbol']} - {row['company_name']}")
            output.append(f"   Rank Score: {row['rank_score']:.2f} | Market Cap: {format_market_cap(row['market_cap'])}")
            
            # Format P/E ratio properly
            pe_value = row.get('pe_ratio', None)
            pe_str = f"{pe_value:.2f}" if pd.notna(pe_value) else "N/A"
            
            output.append(f"   P/E: {pe_str} | "
                         f"Profit Margin: {row['profit_margin']*100:.2f}% | "
                         f"Revenue Growth: {row['revenue_growth']*100:.2f}%")
            output.append(f"   Quality: {row['quality_score']:.1f} | Value: {row['value_score']:.1f} | "
                         f"Growth: {row['growth_score']:.1f} | Momentum: {row['momentum_score']:.1f}")
            output.append(f"   Risk: {row['risk_category']} | Profitability: {row['profitability_status']}")
            output.append("")
        
        output.append("=" * 100)
        output.append("")
        
        return "\n".join(output)
    
    def generate_investment_thesis(self, category_result: dict) -> str:
        """Generate investment thesis for top picks"""
        
        output = []
        
        output.append(f"\nINVESTMENT THESIS - {category_result['description']}")
        output.append("-" * 100)
        output.append("")
        
        top3 = category_result['top_picks'].head(3)
        
        # Overall thesis
        avg_score = category_result['statistics']['avg_composite_score']
        
        if avg_score >= 60:
            outlook = "Strong opportunities with solid fundamentals"
        elif avg_score >= 50:
            outlook = "Moderate opportunities with selective picks"
        else:
            outlook = "Challenging environment, focus on quality"
        
        output.append(f"Market Outlook: {outlook}")
        output.append("")
        
        # Top pick recommendation
        top1 = top3.iloc[0]
        output.append(f"PRIMARY RECOMMENDATION: {top1['symbol']} - {top1['company_name']}")
        output.append(f"  Why: Highest overall score ({top1['rank_score']:.2f}) combining strong fundamentals,")
        output.append(f"       attractive valuation, and positive momentum. {top1['profitability_status']} with")
        output.append(f"       {top1['profit_margin']*100:.1f}% margins and {top1['revenue_growth']*100:.1f}% growth.")
        output.append("")
        
        # Alternative picks
        if len(top3) > 1:
            output.append("ALTERNATIVE PICKS:")
            for i, (_, row) in enumerate(top3.iloc[1:].iterrows(), 2):
                output.append(f"  {i}. {row['symbol']}: Strong {self._get_strength(row)} profile")
        
        output.append("")
        
        return "\n".join(output)
    
    def _get_strength(self, row: pd.Series) -> str:
        """Identify primary strength of a company"""
        
        scores = {
            'quality': row['quality_score'],
            'value': row['value_score'],
            'growth': row['growth_score'],
            'momentum': row['momentum_score']
        }
        
        return max(scores, key=scores.get)
    
    def create_portfolio_summary(self, all_results: dict) -> str:
        """Create comprehensive portfolio summary"""
        
        output = []
        
        output.append("\n")
        output.append("=" * 100)
        output.append("HNI INVESTMENT PORTFOLIO RECOMMENDATIONS")
        output.append("AI-Powered Stock Analysis & Ranking System")
        output.append("=" * 100)
        output.append("")
        
        # Executive summary
        output.append("EXECUTIVE SUMMARY")
        output.append("-" * 100)
        output.append("")
        output.append(f"Total Universe: {len(self.df)} companies analyzed")
        output.append(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
        output.append("")
        output.append("Portfolio Allocation Recommendations:")
        output.append(f"  • Magnificent 7:      All 7 companies ranked")
        output.append(f"  • Giant Cap (>$500B): Top 5 of {all_results['giant']['total_companies']} analyzed")
        output.append(f"  • Large Cap ($100B-$500B): Top 7 of {all_results['large']['total_companies']} analyzed")
        output.append(f"  • Mid Cap (<$100B): Top 10 of {all_results['mid']['total_companies']} analyzed")
        output.append("")
        output.append("=" * 100)
        output.append("")
        
        return "\n".join(output)

# Global instance
portfolio_ranker = PortfolioRanker()
