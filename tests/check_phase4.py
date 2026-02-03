import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.ml_alpha import MLAlphaStrategy
from ai.regime_detection import RegimeDetector
from backtesting.engine import BacktestEngine

def main():
    print("=== Phase 4 Verification: AI & ML ===")
    
    # 1. Ingest Data
    ingestion = DataIngestion()
    # Using SPY using a longer window for ML training
    data = ingestion.fetch_data(tickers=['SPY'], start_date='2018-01-01', end_date='2023-01-01')
    
    print("Data Head:")
    print(data['SPY'].head())
    print("Data Tail (checking for anomaly):")
    print(data['SPY'].tail(15))
    
    # 2. Test Feature Engineering & ML Strategy
    print("\nTraining ML Alpha Strategy...")
    strategy = MLAlphaStrategy()
    
    # This will internally train on 70% and predict on 30%
    # But generate_signals returns dataframe for whole period
    if 'SPY' not in data:
         print("Failed to fetch SPY data.. exiting")
         return 

    # 3. Regime Detection
    print("\nRunning Regime Detection...")
    spy_df = data['SPY']
    returns = spy_df['Close'].pct_change().dropna()
    
    regime_detector = RegimeDetector(n_components=2)
    regimes = regime_detector.fit_predict(returns)
    
    print("Regime Counts:")
    print(regimes.value_counts())
    
    # 4. Run Backtest
    print("\nRunning Backtest on ML Signals...")
    engine = BacktestEngine(strategy=strategy, data=data)
    engine.run()
    
    print("\nBacktest Results Head (Note: signals start after train period):")
    print(engine.results.tail())
    
    metrics = engine.get_performance_metrics()
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    main()
