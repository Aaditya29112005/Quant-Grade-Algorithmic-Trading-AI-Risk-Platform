import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ingestion import DataIngestion
from strategies.momentum import MomentumStrategy
from risk.optimizer import PortfolioOptimizer
from strategies.lstm_alpha import LSTMAlphaStrategy

# Page Configuration
st.set_page_config(
    page_title="Quant Hedge Fund Platform",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("💸 Institutional Quant Platform")
st.markdown("### Deep Learning Alpha • Portfolio Optimization • Risk Parity")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# 1. Data Settings
st.sidebar.subheader("1. Universe Selection")
ticker_input = st.sidebar.text_input("Tickers (comma separated)", value="SPY, AAPL, MSFT, GOOG")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

tickers = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]

# 2. Strategy Settings
st.sidebar.subheader("2. Alpha Strategy")
strategy_type = st.sidebar.selectbox("Select Strategy", 
    ["Momentum (SMA Crossover)", "ML Alpha (Random Forest)", "Deep Learning (LSTM)"])

if strategy_type == "Momentum (SMA Crossover)":
    short_window = st.sidebar.slider("Short Window", 10, 50, 20)
    long_window = st.sidebar.slider("Long Window", 50, 200, 50)
    strategy = MomentumStrategy(short_window, long_window)
elif strategy_type == "ML Alpha (Random Forest)":
    st.sidebar.info("Random Forest on RSI, Volatility, Lags.")
    strategy = MLAlphaStrategy()
else:
    st.sidebar.info("PyTorch LSTM on technical sequences.")
    # Use smaller training window for demo speed if needed
    strategy = LSTMAlphaStrategy(training_window=100)

# 3. Execution Settings
st.sidebar.subheader("3. Execution & Risk")
initial_capital = st.sidebar.number_input("Initial Capital", value=100000.0)
use_latency = st.sidebar.checkbox("Simulate Latency & Slippage", value=True)

run_btn = st.sidebar.button("Run Simulation 🚀", type="primary")

# --- Main Execution ---
if run_btn:
    with st.spinner("Crunching Numbers (AI & Opt)..."):
        # 1. Fetch Data
        ingestion = DataIngestion()
        try:
            data = ingestion.fetch_data(
                tickers=tickers, 
                start_date=str(start_date), 
                end_date=str(end_date)
            )
            
            if not data:
                st.error("No data found!")
                st.stop()
                
            # --- Workflow Switch ---
            # If multiple tickers, show Portfolio Opt. If single, show Backtest.
            
            tabs = st.tabs(["Strategy Backtest", "Portfolio Optimization"])
            
            # Tab 1: Backtest (Run on the first ticker or all independently?)
            # For simplicity, we run the strategy on the FIRST ticker in the list for the deep dive
            with tabs[0]:
                target_ticker = tickers[0]
                st.subheader(f"Strategy Backtest: {target_ticker}")
                
                if target_ticker not in data:
                    st.error(f"Data for {target_ticker} missing.")
                else:
                    # Run Engine on single ticker subset to show curve
                    single_asset_data = {target_ticker: data[target_ticker]}
                    engine = BacktestEngine(
                        strategy=strategy, 
                        data=single_asset_data, 
                        initial_capital=initial_capital,
                        use_latency=use_latency
                    )
                    engine.run()
                    
                    results = engine.results
                    metrics = engine.get_performance_metrics()
                    
                    # Metrics
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Return", f"{metrics.get('Total Return', 0):.2%}")
                    c2.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")
                    c3.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0):.2%}")
                    c4.metric("Volatility", f"{metrics.get('Annualized Volatility', 0):.2%}")
                    
                    # Chart
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(go.Scatter(x=results.index, y=results['PortfolioValue'], name="Strategy Equity"), secondary_y=False)
                    
                    # Benchmark
                    initial_price = data[target_ticker]['Close'].iloc[0]
                    benchmark = (data[target_ticker]['Close'] / initial_price) * initial_capital
                    benchmark = benchmark.reindex(results.index).fillna(method='ffill')
                    fig.add_trace(go.Scatter(x=results.index, y=benchmark, name="Buy & Hold", line=dict(dash='dot')), secondary_y=False)
                    
                    fig.update_layout(title=f"Performance: {strategy.name} on {target_ticker}")
                    st.plotly_chart(fig, use_container_width=True)

            # Tab 2: Portfolio Optimization
            with tabs[1]:
                st.subheader("Modern Portfolio Theory (MPT) Allocation")
                
                if len(tickers) < 2:
                    st.warning("Select at least 2 tickers for Portfolio Optimization.")
                else:
                    # Combine Closes
                    close_df = pd.DataFrame({t: data[t]['Close'] for t in tickers if t in data}).dropna()
                    
                    if close_df.empty:
                        st.error("Not enough overlapping data for optimization.")
                    else:
                        optimizer = PortfolioOptimizer()
                        weights_mv = optimizer.calculate_mean_variance_weights(close_df)
                        weights_rp = optimizer.calculate_risk_parity_weights(close_df)
                        
                        # Visualization of Weights
                        df_weights = pd.DataFrame({
                            "Max Sharpe (Mean-Variance)": weights_mv,
                            "Risk Parity (Equal Risk)": weights_rp
                        })
                        
                        st.bar_chart(df_weights)
                        
                        st.write("### Optimal Weights Allocation")
                        st.dataframe(df_weights.style.format("{:.2%}"))
                        
                        # Correlation Matrix
                        st.write("### Asset Correlation Matrix")
                        corr = close_df.pct_change().corr()
                        fig_corr = go.Figure(data=go.Heatmap(
                            z=corr.values,
                            x=corr.columns,
                            y=corr.columns,
                            colorscale='Viridis'))
                        st.plotly_chart(fig_corr)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

else:
    st.info("👈 Configure parameters and click 'Run Backtest' to start.")

# Footer
st.markdown("---")
st.caption("Built with Python, Streamlit, and Scikit-Learn | Phase 7 Complete")
