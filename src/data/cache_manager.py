"""
Data caching system to avoid redundant API calls
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import pickle
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import logger

class CacheManager:
    """Manages data caching"""
    
    def __init__(self, cache_dir: str = 'data/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_hours = 24  # Cache valid for 24 hours
    
    def get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file"""
        return self.cache_dir / f"{cache_key}.parquet"
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache exists and is not expired"""
        cache_path = self.get_cache_path(cache_key)
        
        if not cache_path.exists():
            return False
        
        # Check file age
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age_hours = (datetime.now() - file_time).total_seconds() / 3600
        
        if age_hours > self.cache_expiry_hours:
            logger.info(f"⏰ Cache expired ({age_hours:.1f} hours old): {cache_key}")
            return False
        
        logger.info(f"✅ Valid cache found ({age_hours:.1f} hours old): {cache_key}")
        return True
    
    def save_to_cache(self, df: pd.DataFrame, cache_key: str):
        """Save DataFrame to cache"""
        cache_path = self.get_cache_path(cache_key)
        
        try:
            df.to_parquet(cache_path, index=False)
            logger.info(f"💾 Saved to cache: {cache_key} ({len(df)} rows)")
        except Exception as e:
            logger.error(f"❌ Failed to save cache: {e}")
    
    def load_from_cache(self, cache_key: str) -> pd.DataFrame:
        """Load DataFrame from cache"""
        cache_path = self.get_cache_path(cache_key)
        
        try:
            df = pd.read_parquet(cache_path)
            logger.info(f"📂 Loaded from cache: {cache_key} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load cache: {e}")
            return None
    
    def get_or_fetch(self, cache_key: str, fetch_function, *args, **kwargs) -> pd.DataFrame:
        """
        Get data from cache if valid, otherwise fetch and cache
        
        Args:
            cache_key: Unique identifier for this dataset
            fetch_function: Function to call if cache is invalid
            *args, **kwargs: Arguments to pass to fetch_function
        """
        if self.is_cache_valid(cache_key):
            return self.load_from_cache(cache_key)
        
        logger.info(f"🔄 Fetching fresh data for: {cache_key}")
        df = fetch_function(*args, **kwargs)
        
        if df is not None and not df.empty:
            self.save_to_cache(df, cache_key)
        
        return df
    
    def clear_cache(self, cache_key: str = None):
        """Clear cache (specific key or all)"""
        if cache_key:
            cache_path = self.get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"🗑️ Cleared cache: {cache_key}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.parquet"):
                cache_file.unlink()
            logger.info(f"🗑️ Cleared all cache files")

# Global cache manager instance
cache_manager = CacheManager()