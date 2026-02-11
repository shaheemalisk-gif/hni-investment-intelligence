"""Quick test of data collection pipeline"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.data.collectors import StockDataCollector
import pandas as pd

def main():
    print("\n" + "="*80)
    print("🚀 HNI INVESTMENT ANALYZER - DATA COLLECTION TEST")
    print("="*80 + "\n")
    
    collector = StockDataCollector()
    
    test_symbols = ['NVDA', 'AAPL', 'MSFT']
    
    print(f"📊 Fetching data for: {', '.join(test_symbols)}")
    print("⏳ This will take ~10-15 seconds...\n")
    
    df = collector.batch_fetch(test_symbols)
    
    print("\n" + "="*80)
    print("✅ DATA COLLECTION SUCCESSFUL!")
    print("="*80 + "\n")
    
    print("KEY METRICS:")
    print("-" * 80)
    
    for idx, row in df.iterrows():
        print(f"\n{row['symbol']} - {row['company_name']}")
        print(f"  Price: ${row['current_price']:.2f}")
        print(f"  Market Cap: ${row['market_cap']/1e9:.2f}B")
        print(f"  P/E Ratio: {row['pe_ratio']:.2f}")
        print(f"  Profit Margin: {row['profit_margin']*100:.2f}%")
        print(f"  Beta: {row['beta']:.2f}")
    
    output_file = 'data/processed/test_results.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*80)
    print(f"💾 Data saved to: {output_file}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()