"""
Update category files with engineered features
"""

import pandas as pd
from src.data.universe import universe_builder

print("\n" + "="*80)
print("🔄 UPDATING CATEGORY FILES WITH ENGINEERED FEATURES")
print("="*80 + "\n")

# Load the full engineered dataset
print("Loading engineered dataset...")
df_full = pd.read_csv('data/processed/stock_universe_engineered.csv')
print(f"Loaded {len(df_full)} companies with {len(df_full.columns)} features")

# Recreate categories with all features
print("\nRecreating category files...")
categories = universe_builder.categorize_by_market_cap(df_full)

for cat_name, cat_df in categories.items():
    filename = f'data/processed/category_{cat_name}.csv'
    cat_df.to_csv(filename, index=False)
    print(f"  ✓ Updated {cat_name}: {len(cat_df)} companies with {len(cat_df.columns)} features")

print("\n" + "="*80)
print("✅ CATEGORY FILES UPDATED!")
print("="*80 + "\n")

# Verify the update
print("Verifying composite_score is present...")
for cat_name in ['mag7', 'giant', 'large', 'mid']:
    cat_df = pd.read_csv(f'data/processed/category_{cat_name}.csv')
    if 'composite_score' in cat_df.columns:
        print(f"  ✓ {cat_name}: composite_score present (avg: {cat_df['composite_score'].mean():.2f})")
    else:
        print(f"  ✗ {cat_name}: composite_score MISSING!")

print("\n✅ Ready to generate portfolio!\n")