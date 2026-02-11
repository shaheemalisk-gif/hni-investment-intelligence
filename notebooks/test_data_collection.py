import sys
sys.path.append('.')

from src.data.collectors import StockDataCollector
from src.utils.logger import logger

def main():
    logger.info("🚀 Starting data collection test...")
    
    collector = StockDataCollector()
    
    # Test symbols
    test_symbols = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']
    
    print(f"\n📊 Fetching data for: {', '.join(test_symbols)}\n")
    
    df = collector.batch_fetch(test_symbols)
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(df[['symbol', 'company_name', 'market_cap', 'pe_ratio', 
              'profit_margin', 'revenue_growth', 'beta']].to_string())
    print("="*80)
    
    # Save results
    df.to_csv('data/processed/test_results.csv', index=False)
    logger.info("✅ Test complete! Data saved to data/processed/test_results.csv")

if __name__ == "__main__":
    main()