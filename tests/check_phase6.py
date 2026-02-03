import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.momentum import MomentumStrategy
from backtesting.engine import BacktestEngine

def main():
    print("=== Phase 6 Verification: Execution Microstructure ===")
    
    # 1. Ingest Data
    ingestion = DataIngestion()
    data = ingestion.fetch_data(tickers=['AAPL'], start_date='2019-01-01', end_date='2022-01-01')
    
    # 2. Strategy
    strategy = MomentumStrategy(short_window=20, long_window=50)
    
    # 3. Backtest 1: Perfect Execution (Benchmark)
    print("\nRunning Backtest: NO Latency...")
    engine_perfect = BacktestEngine(strategy=strategy, data=data, use_latency=False)
    engine_perfect.run()
    res_perfect = engine_perfect.get_performance_metrics()
    
    # 4. Backtest 2: Realistic Execution
    print("\nRunning Backtest: WITH Latency & Slippage...")
    print("Simulating 100ms latency + Volatility based slippage...")
    engine_real = BacktestEngine(strategy=strategy, data=data, use_latency=True)
    engine_real.run()
    res_real = engine_real.get_performance_metrics()
    
    # 5. Compare
    print("\n--- Impact Analysis ---")
    print(f"Total Return (Perfect): {res_perfect['Total Return']:.4%}")
    print(f"Total Return (Realistic): {res_real['Total Return']:.4%}")
    
    cost_impact = res_perfect['Total Return'] - res_real['Total Return']
    print(f"Slippage & Latency Cost: {cost_impact:.4%}")
    
    if cost_impact > 0:
        print("PASS: Realistic simulation correctly degraded performance.")
    else:
        print("WARNING: Performance didn't degrade? Check slippage model.")

if __name__ == "__main__":
    main()
