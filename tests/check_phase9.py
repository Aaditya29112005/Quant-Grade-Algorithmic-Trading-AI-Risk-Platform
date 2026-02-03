import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.lstm_alpha import LSTMAlphaStrategy
from risk.optimizer import PortfolioOptimizer
from backtesting.engine import BacktestEngine

def main():
    print("=== Phase 9 Verification: Deep Learning & Portfolio Opt ===")
    
    ingestion = DataIngestion()
    
    # 1. Test Portfolio Optimizer
    print("\n[1] Testing Mean-Variance Optimization...")
    tickers = ['AAPL', 'MSFT', 'GOOG', 'SPY']
    data_dict = ingestion.fetch_data(tickers, start_date='2020-01-01', end_date='2022-01-01')
    
    # Create combined close price dataframe
    close_df = pd.DataFrame({t: data_dict[t]['Close'] for t in tickers}).dropna()
    
    optimizer = PortfolioOptimizer()
    weights_mv = optimizer.calculate_mean_variance_weights(close_df)
    weights_rp = optimizer.calculate_risk_parity_weights(close_df)
    
    print("Mean-Variance Weights (Max Sharpe):")
    for t, w in weights_mv.items():
        print(f"  {t}: {w:.4f}")
        
    print("\nRisk Parity Weights (Inverse Vol):")
    for t, w in weights_rp.items():
        print(f"  {t}: {w:.4f}")
        
    # 2. Test LSTM Strategy
    print("\n[2] Testing LSTM Alpha Strategy (PyTorch)...")
    # Using single ticker for backtest
    spy_data = {'SPY': data_dict['SPY']} 
    
    # Run small backtest (Train on 100 days to ensure we have enough data in 2 years)
    strategy = LSTMAlphaStrategy(training_window=100)
    
    engine = BacktestEngine(strategy=strategy, data=spy_data, use_latency=False)
    engine.run()
    
    metrics = engine.get_performance_metrics()
    print("\nLSTM Performance (SPY):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

if __name__ == "__main__":
    main()
