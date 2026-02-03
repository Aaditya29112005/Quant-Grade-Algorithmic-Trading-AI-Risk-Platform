import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.momentum import MomentumStrategy
from backtesting.engine import BacktestEngine
from risk.var_cvar import RiskMetrics

def main():
    print("=== Phase 5 Verification: Risk Management ===")
    
    # 1. Ingest Data (AAPL 2020 Volatility)
    ingestion = DataIngestion()
    # 2020 was high vol due to Covid. 2021 was lower.
    data = ingestion.fetch_data(tickers=['AAPL'], start_date='2019-01-01', end_date='2022-01-01')
    
    # 2. Strategy
    strategy = MomentumStrategy(short_window=20, long_window=50)
    
    # 3. Backtest with Risk Manager (Vol Target 20%)
    print("\nRunning Backtest with Volatility Targeting (Target=20%)...")
    engine = BacktestEngine(strategy=strategy, data=data)
    engine.run()
    
    metrics = engine.get_performance_metrics()
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    # 4. Check Risk Metrics (VaR)
    if not engine.results.empty:
        rets = engine.results['Returns']
        var_95 = RiskMetrics.calculate_var(rets, 0.95)
        cvar_95 = RiskMetrics.calculate_cvar(rets, 0.95)
        
        print(f"\nHistorical VaR (95%): {var_95:.2%}")
        print(f"Historical CVaR (95%): {cvar_95:.2%}")

if __name__ == "__main__":
    main()
