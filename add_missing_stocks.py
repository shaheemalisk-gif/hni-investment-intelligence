"""
Add missing stocks (NVDA, TSLA) to the universe
"""

import sys
sys.path.append('.')

import pandas as pd
from src.data.collectors import StockDataCollector
from src.analysis.feature_engineering import FeatureEngineer
from src.data.universe import universe_builder

def main():
    print("\n" + "="*80)
    print("➕ ADDING MISSING STOCKS TO UNIVERSE")
    print("="*80 + "\n")
    
    # Load existing data
    print("Loading existing universe...")
    df_existing = pd.read_csv('data/processed/stock_universe_engineered.csv')
    print(f"Current companies: {len(df_existing)}")
    
    # Stocks to add
    missing_stocks = ['NVDA', 'TSLA']
    
    print(f"\nAdding: {', '.join(missing_stocks)}")
    
    # Fetch new stocks
    collector = StockDataCollector()
    print("\nFetching data...")
    df_new = collector.batch_fetch(missing_stocks)
    
    # Add sector category
    df_new['sector_category'] = df_new['symbol'].apply(universe_builder.get_sector_for_symbol)
    
    # Add industry comparisons
    df_new = collector.add_industry_comparisons(df_new)
    
    # Apply feature engineering
    print("\nApplying feature engineering...")
    feature_engineer = FeatureEngineer()
    df_new = feature_engineer.engineer_all_features(df_new)
    
    # Combine with existing data
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    
    # Remove duplicates (in case NVDA/TSLA were already there somehow)
    df_combined = df_combined.drop_duplicates(subset=['symbol'], keep='last')
    
    print(f"\n✅ Total companies: {len(df_combined)}")
    
    # Save updated universe
    df_combined.to_csv('data/processed/stock_universe_full.csv', index=False)
    df_combined.to_csv('data/processed/stock_universe_engineered.csv', index=False)
    
    # Update cache
    df_combined.to_parquet('data/cache/stock_universe_full.parquet', index=False)
    
    # Update categories
    print("\nUpdating categories...")
    categories = universe_builder.categorize_by_market_cap(df_combined)
    
    for cat_name, cat_df in categories.items():
        cat_file = f'data/processed/category_{cat_name}.csv'
        cat_df.to_csv(cat_file, index=False)
        print(f"  ✓ {cat_name}: {len(cat_df)} companies")
    
    print("\n" + "="*80)
    print("🎉 SUCCESSFULLY ADDED MISSING STOCKS!")
    print("="*80)
    print(f"\nUpdated files:")
    print("  - stock_universe_full.csv")
    print("  - stock_universe_engineered.csv")
    print("  - category_mag7.csv")
    print("  - All other category files")
    
    # Show new stocks
    print("\n" + "-"*80)
    print("NEW STOCKS ADDED:")
    print("-"*80)
    
    for symbol in missing_stocks:
        stock = df_combined[df_combined['symbol'] == symbol].iloc[0]
        print(f"\n{symbol} - {stock['company_name']}")
        print(f"  Market Cap: ${stock['market_cap']/1e9:.2f}B")
        print(f"  Health Score: {stock.get('composite_score', 0):.2f}")
        print(f"  Category: {stock['sector_category']}")

if __name__ == "__main__":
    main()