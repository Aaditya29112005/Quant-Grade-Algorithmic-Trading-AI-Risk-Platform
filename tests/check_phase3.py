import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.momentum import MomentumStrategy
from backtesting.engine import BacktestEngine

def main():
    # 1. Ingest Data
    ingestion = DataIngestion()
    # Using AAPL for a 5 year period
    data = ingestion.fetch_data(tickers=['AAPL'], start_date='2020-01-01', end_date='2023-01-01')
    
    print("\nData Head:")
    for ticker, df in data.items():
        print(f"--- {ticker} ---")
        print(df.head())
    
    # 2. Define Strategy
    strategy = MomentumStrategy(short_window=50, long_window=200)
    
    # 3. Run Backtest
    engine = BacktestEngine(strategy=strategy, data=data)
    engine.run()
    
    # 4. Show Results
    print("\nBacktest Results Head:")
    print(engine.results.head())
    
    metrics = engine.get_performance_metrics()
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    main()
