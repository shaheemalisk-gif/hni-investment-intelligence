"""
Stock Universe Manager - Builds and maintains company lists
"""

import pandas as pd
import yfinance as yf
from typing import List, Dict
import yaml
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import logger

class UniverseBuilder:
    """Builds categorized stock universe"""
    
    def __init__(self):
        self.mag7 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']
        
        # Comprehensive stock lists by sector
        self.universe = {
            'tech': [
                'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA' , 'ORCL', 'CSCO', 'ADBE',
                'CRM', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO', 'NOW', 'INTU',
                'AMAT', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS', 'MCHP', 'NXPI',
                'PANW', 'FTNT', 'CRWD', 'ZS', 'DDOG', 'NET'
            ],
            'healthcare': [
                'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT',
                'DHR', 'AMGN', 'GILD', 'CVS', 'MDT', 'REGN', 'ISRG', 'VRTX',
                'CI', 'HUM', 'BSX', 'ELV'
            ],
            'finance': [
                'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'V', 'MA',
                'C', 'SCHW', 'AXP', 'USB', 'PNC', 'TFC', 'COF', 'BK',
                'AIG', 'MET', 'PRU', 'ALL'
            ],
            'consumer': [
                'WMT', 'AMZN', 'HD', 'MCD', 'NKE', 'COST', 'SBUX', 'TGT',
                'LOW', 'TJX', 'DG', 'ROST', 'YUM', 'CMG', 'ORLY', 'KMX'
            ],
            'consumer_staples': [
                'PG', 'KO', 'PEP', 'PM', 'COST', 'MDLZ', 'MO', 'CL',
                'KMB', 'GIS', 'HSY', 'K', 'SYY', 'TSN'
            ],
            'energy': [
                'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'PSX',
                'VLO', 'OXY', 'HAL', 'BKR', 'WMB', 'KMI'
            ],
            'industrials': [
                'BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX', 'LMT', 'DE',
                'MMM', 'UNP', 'ETN', 'ADP', 'EMR', 'ITW', 'CSX', 'NSC'
            ],
            'materials': [
                'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'DD', 'DOW',
                'NUE', 'VMC', 'MLM'
            ],
            'real_estate': [
                'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'DLR', 'O',
                'SBAC', 'AVB'
            ],
            'utilities': [
                'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL',
                'PCG', 'ED'
            ],
            'telecom': [
                'T', 'VZ', 'TMUS', 'CHTR'
            ]
        }
    
    def get_all_symbols(self) -> List[str]:
        """Get all unique symbols across sectors"""
        all_symbols = set()
        for sector_symbols in self.universe.values():
            all_symbols.update(sector_symbols)
        return sorted(list(all_symbols))
    
    def get_sector_for_symbol(self, symbol: str) -> str:
        """Get sector for a given symbol"""
        for sector, symbols in self.universe.items():
            if symbol in symbols:
                return sector
        return 'unknown'
    
    def categorize_by_market_cap(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Categorize companies into 4 groups based on market cap
        
        Returns:
            Dictionary with keys: 'mag7', 'giant', 'large', 'mid'
        """
        categories = {}
        
        # Magnificent 7 (explicitly defined)
        categories['mag7'] = df[df['symbol'].isin(self.mag7)].copy()
        
        # Remove mag7 from other categories
        df_remaining = df[~df['symbol'].isin(self.mag7)].copy()
        
        # Giant: >$500B (excluding mag7)
        categories['giant'] = df_remaining[
            df_remaining['market_cap'] > 500_000_000_000
        ].copy()
        
        # Large: $100B - $500B
        categories['large'] = df_remaining[
            (df_remaining['market_cap'] >= 100_000_000_000) &
            (df_remaining['market_cap'] <= 500_000_000_000)
        ].copy()
        
        # Mid: <$100B
        categories['mid'] = df_remaining[
            df_remaining['market_cap'] < 100_000_000_000
        ].copy()
        
        # Log statistics
        logger.info(f"📊 Categorization Complete:")
        logger.info(f"  Magnificent 7: {len(categories['mag7'])} companies")
        logger.info(f"  Giant (>$500B): {len(categories['giant'])} companies")
        logger.info(f"  Large ($100B-$500B): {len(categories['large'])} companies")
        logger.info(f"  Mid (<$100B): {len(categories['mid'])} companies")
        
        return categories
    
    def get_symbols_by_category(self, target_counts: Dict[str, int] = None) -> Dict[str, List[str]]:
        """
        Get symbols to fetch for each category
        
        Args:
            target_counts: Dict with target number per category
                          e.g., {'giant': 20, 'large': 30, 'mid': 50}
        """
        if target_counts is None:
            target_counts = {
                'mag7': 7,
                'giant': 15,  # Will get top by market cap
                'large': 30,
                'mid': 50
            }
        
        all_symbols = self.get_all_symbols()
        
        return {
            'all_symbols': all_symbols,
            'target_counts': target_counts
        }
    
    def calculate_sector_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate sector-level statistics for benchmarking
        """
        # Add sector column
        df['sector_category'] = df['symbol'].apply(self.get_sector_for_symbol)
        
        # Group by sector
        sector_stats = df.groupby('sector_category').agg({
            'market_cap': ['mean', 'median'],
            'pe_ratio': ['mean', 'median'],
            'profit_margin': ['mean', 'median'],
            'revenue_growth': ['mean', 'median'],
            'debt_to_equity': ['mean', 'median'],
            'roe': ['mean', 'median'],
            'beta': ['mean', 'median']
        }).round(2)
        
        sector_stats.columns = ['_'.join(col) for col in sector_stats.columns]
        
        logger.info(f"📈 Calculated stats for {len(sector_stats)} sectors")
        
        return sector_stats

# Create global instance
universe_builder = UniverseBuilder()