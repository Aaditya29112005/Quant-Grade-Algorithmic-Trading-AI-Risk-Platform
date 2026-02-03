import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import Strategy
from backtesting.metrics import calculate_metrics

class BacktestEngine:
    def __init__(self, strategy: Strategy, data: Dict[str, pd.DataFrame], initial_capital: float = 100000.0):
        """
        Args:
            strategy: Instance of a Strategy class.
            data: Market data (Dict mapping ticker -> DataFrame).
            initial_capital: Starting portfolio value.
        """
        self.strategy = strategy
        self.data = data
        self.initial_capital = initial_capital
        self.portfolio_value = []
        self.positions = {} # Current holding quantity per ticker
        self.cash = initial_capital
        self.history = []

    def run(self):
        """
        Executes the backtest using an event-driven loop (bar-by-bar).
        """
        print(f"Running backtest for {self.strategy.name}...")
        
        tickers = list(self.data.keys())
        
        if not tickers:
            print("No data available for backtesting.")
            return

        # Union of all dates
        all_dates = sorted(list(set().union(*[df.index for df in self.data.values()])))
        
        # Calculate Signals per ticker
        all_signals = {}
        for ticker in tickers:
            ticker_data = self.data[ticker]
            all_signals[ticker] = self.strategy.generate_signals(ticker_data)
        
        # Iterating through time
        for date in all_dates:
            daily_portfolio_value = self.cash
            
            for ticker in tickers:
                # Check if we have data and signals for this date
                if date not in self.data[ticker].index or date not in all_signals[ticker].index:
                    # If data missing, we just hold position
                    current_price = 0 # Cannot valuate accurately if missing, or use last known.
                    # For simple backtest, use last known if available? 
                    # Simpler: just skip valuation for this ticker logic update, but we need price for portfolio value.
                    # We can assume 'ffill' was done.
                    
                    # Try to get last price
                    try:
                        current_price = self.data[ticker].loc[:date].iloc[-1]['Close']
                    except:
                         current_price = 0
                else:
                    current_price = self.data[ticker].loc[date, 'Close']
                    
                    # Signal Handling
                    signal_row = all_signals[ticker].loc[date]
                    target_position = signal_row['Signal']
                    
                    current_qty = self.positions.get(ticker, 0)
                    
                    if target_position == 1 and current_qty == 0:
                        # Buy
                        if current_price > 0:
                            shares_to_buy = int(self.cash // current_price)
                            if shares_to_buy > 0:
                                cost = shares_to_buy * current_price
                                self.cash -= cost
                                self.positions[ticker] = shares_to_buy
                    
                    elif target_position == 0 and current_qty > 0:
                        # Sell
                        if current_price > 0:
                            revenue = current_qty * current_price
                            self.cash += revenue
                            self.positions[ticker] = 0
                
                # Update Valuation
                if current_price > 0:
                    daily_portfolio_value += self.positions.get(ticker, 0) * current_price
            
            self.portfolio_value.append({'Date': date, 'PortfolioValue': daily_portfolio_value})
            
        self.results = pd.DataFrame(self.portfolio_value).set_index('Date')
        self.results['Returns'] = self.results['PortfolioValue'].pct_change().fillna(0)
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        if not hasattr(self, 'results'):
            return {}
        return calculate_metrics(self.results['Returns'])
