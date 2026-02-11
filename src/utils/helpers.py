import pandas as pd
import numpy as np
from typing import List, Dict, Union
import time
from functools import wraps
from src.utils.logger import logger

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate
    """
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return 0.0
    return (pow(end_value / start_value, 1 / years) - 1) * 100

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe Ratio (risk-adjusted return)
    """
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    if excess_returns.std() == 0:
        return 0.0
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

def normalize_values(values: Union[pd.Series, np.ndarray], 
                     method: str = 'minmax') -> Union[pd.Series, np.ndarray]:
    """
    Normalize values to 0-100 scale
    """
    if method == 'minmax':
        min_val = values.min()
        max_val = values.max()
        if max_val == min_val:
            return pd.Series([50] * len(values)) if isinstance(values, pd.Series) else np.array([50] * len(values))
        normalized = ((values - min_val) / (max_val - min_val)) * 100
    elif method == 'zscore':
        normalized = ((values - values.mean()) / values.std()) * 10 + 50
        normalized = np.clip(normalized, 0, 100)
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return normalized

def format_market_cap(market_cap: float) -> str:
    """
    Format market cap in human-readable format
    """
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def calculate_percentile_rank(value: float, series: pd.Series) -> float:
    """
    Calculate percentile rank of a value in a series (0-100)
    """
    return (series < value).sum() / len(series) * 100