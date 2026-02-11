import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from src.utils.logger import logger
from src.utils.helpers import retry_on_failure
from src.utils.config import config

class StockDataCollector:
    """
    Collects comprehensive stock data from multiple sources
    """
    
    def __init__(self):
        self.cache_enabled = config.get('data_collection.cache_enabled', True)
        self.rate_limit_delay = config.get('data_collection.rate_limit_delay', 1.0)
        self.historical_years = config.get('data_collection.historical_years', 5)
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def fetch_ticker_info(self, symbol: str) -> Dict:
        """
        Fetch comprehensive ticker information
        """
        logger.info(f"Fetching data for {symbol}")
        
        ticker = yf.Ticker(symbol)
        
        try:
            # Basic info
            info = ticker.info
            
            # Historical prices
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * self.historical_years)
            hist = ticker.history(start=start_date, end=end_date)
            
            # Financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Quarterly data for recent trends
            quarterly_financials = ticker.quarterly_financials
            
            data = {
                'symbol': symbol,
                'info': info,
                'historical_prices': hist,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'quarterly_financials': quarterly_financials,
                'fetch_timestamp': datetime.now()
            }
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            logger.info(f"✅ Successfully fetched data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
            raise
    
    def extract_key_metrics(self, ticker_data: Dict) -> Dict:
        """
        Extract key financial metrics from raw ticker data
        """
        info = ticker_data['info']
        hist = ticker_data['historical_prices']
        
        metrics = {
            'symbol': ticker_data['symbol'],
            
            # Market Data
            'current_price': info.get('currentPrice', np.nan),
            'market_cap': info.get('marketCap', np.nan),
            'enterprise_value': info.get('enterpriseValue', np.nan),
            
            # Valuation Ratios
            'pe_ratio': info.get('trailingPE', np.nan),
            'forward_pe': info.get('forwardPE', np.nan),
            'peg_ratio': info.get('pegRatio', np.nan),
            'price_to_book': info.get('priceToBook', np.nan),
            'price_to_sales': info.get('priceToSalesTrailing12Months', np.nan),
            'ev_to_revenue': info.get('enterpriseToRevenue', np.nan),
            'ev_to_ebitda': info.get('enterpriseToEbitda', np.nan),
            
            # Profitability
            'profit_margin': info.get('profitMargins', np.nan),
            'operating_margin': info.get('operatingMargins', np.nan),
            'gross_margin': info.get('grossMargins', np.nan),
            'roe': info.get('returnOnEquity', np.nan),
            'roa': info.get('returnOnAssets', np.nan),
            
            # Growth
            'revenue_growth': info.get('revenueGrowth', np.nan),
            'earnings_growth': info.get('earningsGrowth', np.nan),
            
            # Financial Health
            'debt_to_equity': info.get('debtToEquity', np.nan),
            'current_ratio': info.get('currentRatio', np.nan),
            'quick_ratio': info.get('quickRatio', np.nan),
            
            # Cash Flow
            'free_cash_flow': info.get('freeCashflow', np.nan),
            'operating_cash_flow': info.get('operatingCashflow', np.nan),
            
            # Risk
            'beta': info.get('beta', np.nan),
            
            # Other
            'dividend_yield': info.get('dividendYield', np.nan),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            
            # Company Info
            'company_name': info.get('longName', info.get('shortName', 'Unknown')),
            'country': info.get('country', 'Unknown'),
        }
        
        # Calculate additional metrics from price history
        if not hist.empty:
            returns = hist['Close'].pct_change().dropna()
            
            metrics['volatility_30d'] = returns.tail(30).std() * np.sqrt(252) * 100  # Annualized
            metrics['volatility_90d'] = returns.tail(90).std() * np.sqrt(252) * 100
            metrics['max_drawdown'] = self._calculate_max_drawdown(hist['Close'])
            metrics['sharpe_ratio'] = self._calculate_sharpe(returns)
            
            # Momentum indicators
            metrics['return_1m'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100 if len(hist) > 21 else np.nan
            metrics['return_3m'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1) * 100 if len(hist) > 63 else np.nan
            metrics['return_6m'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-126] - 1) * 100 if len(hist) > 126 else np.nan
            metrics['return_1y'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-252] - 1) * 100 if len(hist) > 252 else np.nan
        
        return metrics
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100  # As percentage
    
    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0.0
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    def batch_fetch(self, symbols: List[str]) -> pd.DataFrame:
        """
        Fetch data for multiple symbols and return as DataFrame
        """
        all_metrics = []
        
        for symbol in symbols:
            try:
                ticker_data = self.fetch_ticker_info(symbol)
                metrics = self.extract_key_metrics(ticker_data)
                all_metrics.append(metrics)
            except Exception as e:
                logger.warning(f"Skipping {symbol} due to error: {e}")
                continue
        
        df = pd.DataFrame(all_metrics)
        logger.info(f"✅ Successfully fetched data for {len(df)} / {len(symbols)} symbols")
        
        return df

    def fetch_universe(self, max_symbols: int = 100) -> pd.DataFrame:
        """
        Fetch comprehensive stock universe
        
        Args:
            max_symbols: Maximum number of symbols to fetch
        """
        from src.data.universe import universe_builder
        
        all_symbols = universe_builder.get_all_symbols()
        
        # Limit to max_symbols if specified
        if max_symbols and len(all_symbols) > max_symbols:
            logger.info(f"⚠️ Limiting fetch to {max_symbols} symbols (from {len(all_symbols)} total)")
            all_symbols = all_symbols[:max_symbols]
        
        logger.info(f"🚀 Fetching {len(all_symbols)} symbols...")
        logger.info(f"⏰ Estimated time: {len(all_symbols) * 2 / 60:.1f} minutes")
        
        df = self.batch_fetch(all_symbols)
        
        # Add sector information
        df['sector_category'] = df['symbol'].apply(universe_builder.get_sector_for_symbol)
        
        return df
    
    def add_industry_comparisons(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add industry comparison metrics (percentile ranks within sector)
        """
        from src.data.universe import universe_builder
        
        # Calculate sector stats
        sector_stats = universe_builder.calculate_sector_stats(df)
        
        # Add percentile ranks within sector
        for metric in ['pe_ratio', 'profit_margin', 'revenue_growth', 'roe', 'beta']:
            if metric in df.columns:
                # Calculate percentile rank within sector
                df[f'{metric}_sector_rank'] = df.groupby('sector_category')[metric].rank(pct=True) * 100
        
        logger.info("✅ Added industry comparison metrics")
        
        return df
    
    def calculate_growth_trends(self, ticker_data: Dict) -> Dict:
        """
        Calculate multi-year growth trends
        """
        hist = ticker_data['historical_prices']
        
        trends = {}
        
        if not hist.empty and len(hist) > 252:
            prices = hist['Close']
            
            # 3-year CAGR
            if len(prices) >= 756:  # 3 years
                start_price = prices.iloc[-756]
                end_price = prices.iloc[-1]
                trends['cagr_3y'] = (pow(end_price / start_price, 1/3) - 1) * 100
            
            # 5-year CAGR
            if len(prices) >= 1260:  # 5 years
                start_price = prices.iloc[-1260]
                end_price = prices.iloc[-1]
                trends['cagr_5y'] = (pow(end_price / start_price, 1/5) - 1) * 100
            
            # Price momentum (vs moving averages)
            current_price = prices.iloc[-1]
            ma_50 = prices.tail(50).mean()
            ma_200 = prices.tail(200).mean()
            
            trends['price_vs_ma50'] = ((current_price / ma_50) - 1) * 100
            trends['price_vs_ma200'] = ((current_price / ma_200) - 1) * 100
        
        return trends    