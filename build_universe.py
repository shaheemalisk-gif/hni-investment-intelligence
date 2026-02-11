"""
Build complete stock universe with all metrics
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
from src.data.collectors import StockDataCollector
from src.data.universe import universe_builder
from src.data.cache_manager import cache_manager
from src.utils.logger import logger
from src.utils.helpers import format_market_cap

def main():
    print("\n" + "="*80)
    print("🌍 BUILDING COMPLETE STOCK UNIVERSE")
    print("="*80 + "\n")
    
    collector = StockDataCollector()
    
    # Option 1: Use cache if available
    print("Checking for cached data...\n")
    
    df = cache_manager.get_or_fetch(
        cache_key='stock_universe_full',
        fetch_function=collector.fetch_universe,
        max_symbols=100  # Limit to 100 for testing, remove for full universe
    )
    
    if df is None or df.empty:
        logger.error("❌ Failed to fetch data")
        return
    
    print(f"\n✅ Loaded {len(df)} companies\n")
    
    # Add industry comparisons
    df = collector.add_industry_comparisons(df)
    
    # Categorize by market cap
    categories = universe_builder.categorize_by_market_cap(df)
    
    # Display summary statistics
    print("\n" + "="*80)
    print("📊 UNIVERSE SUMMARY")
    print("="*80 + "\n")
    
    print(f"Total companies: {len(df)}")
    print(f"Sectors covered: {df['sector_category'].nunique()}")
    print(f"\nMarket Cap Distribution:")
    print(f"  Magnificent 7:    {len(categories['mag7'])} companies")
    print(f"  Giants (>$500B):  {len(categories['giant'])} companies")
    print(f"  Large ($100-500B): {len(categories['large'])} companies")
    print(f"  Mid (<$100B):     {len(categories['mid'])} companies")
    
    # Top 10 by market cap
    print("\n" + "-"*80)
    print("TOP 10 COMPANIES BY MARKET CAP")
    print("-"*80)
    
    top_10 = df.nlargest(10, 'market_cap')[
        ['symbol', 'company_name', 'market_cap', 'sector_category']
    ]
    
    for idx, row in top_10.iterrows():
        print(f"{row['symbol']:6s} | {row['company_name']:40s} | "
              f"{format_market_cap(row['market_cap']):12s} | {row['sector_category']}")
    
    # Sector breakdown
    print("\n" + "-"*80)
    print("SECTOR BREAKDOWN")
    print("-"*80)
    
    sector_counts = df['sector_category'].value_counts()
    for sector, count in sector_counts.items():
        avg_market_cap = df[df['sector_category'] == sector]['market_cap'].mean()
        print(f"{sector:20s} | {count:3d} companies | "
              f"Avg Market Cap: {format_market_cap(avg_market_cap)}")
    
    # Save categorized data
    print("\n" + "="*80)
    print("💾 SAVING CATEGORIZED DATA")
    print("="*80 + "\n")
    
    # Save full dataset
    output_file = 'data/processed/stock_universe_full.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Full universe: {output_file}")
    
    # Save each category separately
    for cat_name, cat_df in categories.items():
        cat_file = f'data/processed/category_{cat_name}.csv'
        cat_df.to_csv(cat_file, index=False)
        print(f"✅ {cat_name:10s}: {cat_file} ({len(cat_df)} companies)")
    
    # Save sector statistics
    sector_stats = universe_builder.calculate_sector_stats(df)
    sector_stats.to_csv('data/processed/sector_benchmarks.csv')
    print(f"✅ Sector stats: data/processed/sector_benchmarks.csv")
    
    print("\n" + "="*80)
    print("🎉 UNIVERSE BUILD COMPLETE!")
    print("="*80 + "\n")
    
    # Display sample from each category
    print("SAMPLES FROM EACH CATEGORY:\n")
    
    for cat_name, cat_df in categories.items():
        if not cat_df.empty:
            print(f"\n{cat_name.upper()} - Top 3:")
            sample = cat_df.nlargest(3, 'market_cap')[
                ['symbol', 'company_name', 'market_cap', 'pe_ratio', 'profit_margin']
            ]
            print(sample.to_string(index=False))

if __name__ == "__main__":
    main()