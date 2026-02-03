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
from strategies.ml_alpha import MLAlphaStrategy
from backtesting.engine import BacktestEngine
from backtesting.metrics import calculate_metrics

# Page Configuration
st.set_page_config(
    page_title="AI Quant Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🤖 AI Algorithmic Trading Platform")
st.markdown("### Feature Engineering • Regime Detection • Risk Management")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# 1. Data Settings
st.sidebar.subheader("1. Data Ingestion")
ticker_input = st.sidebar.text_input("Ticker Symbol", value="SPY")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

# 2. Strategy Settings
st.sidebar.subheader("2. Strategy Logic")
strategy_type = st.sidebar.selectbox("Select Strategy", ["Momentum (SMA Crossover)", "ML Alpha (Random Forest)"])

if strategy_type == "Momentum (SMA Crossover)":
    short_window = st.sidebar.slider("Short Window", 10, 50, 20)
    long_window = st.sidebar.slider("Long Window", 50, 200, 50)
    strategy = MomentumStrategy(short_window, long_window)
else:
    st.sidebar.info("ML Strategy uses Random Forest on RSI, Volatility, and Lags.")
    strategy = MLAlphaStrategy()

# 3. Execution Settings
st.sidebar.subheader("3. Execution & Risk")
initial_capital = st.sidebar.number_input("Initial Capital", value=100000.0)
use_latency = st.sidebar.checkbox("Simulate Latency & Slippage", value=True)

run_btn = st.sidebar.button("Run Backtest 🚀", type="primary")

# --- Main Execution ---
if run_btn:
    with st.spinner("Fetching Data & Running Simulation..."):
        # 1. Fetch Data
        ingestion = DataIngestion()
        try:
            data = ingestion.fetch_data(
                tickers=[ticker_input], 
                start_date=str(start_date), 
                end_date=str(end_date)
            )
            
            if ticker_input not in data or data[ticker_input].empty:
                st.error(f"No data found for {ticker_input}!")
                st.stop()
                
            # 2. Run Engine
            engine = BacktestEngine(
                strategy=strategy, 
                data=data, 
                initial_capital=initial_capital,
                use_latency=use_latency
            )
            engine.run()
            
            # 3. Process Results
            results = engine.results
            metrics = engine.get_performance_metrics()
            
            # --- Visualization ---
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Return", f"{metrics.get('Total Return', 0):.2%}")
            col2.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")
            col3.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0):.2%}")
            col4.metric("Volatility", f"{metrics.get('Annualized Volatility', 0):.2%}")
            
            # Charts
            tab1, tab2 = st.tabs(["Equity Curve", "Drawdown Analysis"])
            
            with tab1:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Portfolio Value
                fig.add_trace(
                    go.Scatter(x=results.index, y=results['PortfolioValue'], name="Portfolio Value"),
                    secondary_y=False
                )
                
                # Benchmark (Buy & Hold) - Normalize to initial capital
                initial_price = data[ticker_input]['Close'].iloc[0]
                benchmark = (data[ticker_input]['Close'] / initial_price) * initial_capital
                # Align dates
                benchmark = benchmark.reindex(results.index).fillna(method='ffill')
                
                fig.add_trace(
                    go.Scatter(x=results.index, y=benchmark, name=f"{ticker_input} Buy & Hold", line=dict(dash='dot')),
                    secondary_y=False
                )
                
                fig.update_layout(title="Portfolio Performance vs Benchmark", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            with tab2:
                # Calculate Drawdown series
                running_max = results['PortfolioValue'].cummax()
                drawdown = (results['PortfolioValue'] - running_max) / running_max
                
                fig_dd = go.Figure()
                fig_dd.add_trace(go.Scatter(x=results.index, y=drawdown, fill='tozeroy', name="Drawdown", line=dict(color='red')))
                fig_dd.update_layout(title="Drawdown Over Time", yaxis_tickformat='.1%', height=400)
                st.plotly_chart(fig_dd, use_container_width=True)
            
            # Logic Explanation
            with st.expander("See Trade Log & Signals"):
                st.dataframe(results.tail(20))
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

else:
    st.info("👈 Configure parameters and click 'Run Backtest' to start.")

# Footer
st.markdown("---")
st.caption("Built with Python, Streamlit, and Scikit-Learn | Phase 7 Complete")
