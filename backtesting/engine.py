import pandas as pd
import numpy as np
from typing import Dict, Any
from strategies.base import Strategy
from risk.manager import RiskManager
from backtesting.metrics import calculate_metrics
from execution.latency_model import LatencyModel

class BacktestEngine:
    def __init__(self, strategy: Strategy, data: Dict[str, pd.DataFrame], initial_capital: float = 100000.0, use_latency: bool = False):
        """
        Args:
           ...
           use_latency: If True, enables latency and slippage simulation.
        """
        self.strategy = strategy
        self.data = data
        self.initial_capital = initial_capital
        self.portfolio_value = []
        self.positions = {} # Current holding quantity per ticker
        self.cash = initial_capital
        self.history = []
        
        # Risk Manager
        self.risk_manager = RiskManager(target_volatility=0.20, max_drawdown_limit=0.25)
        self.peak_equity = initial_capital
        
        # Execution
        self.use_latency = use_latency
        self.latency_model = LatencyModel() if use_latency else None
        
    def run(self):
        # ... (same setup) ...
        print(f"Running backtest for {self.strategy.name} (Latency={'ON' if self.use_latency else 'OFF'})...")
        
        tickers = list(self.data.keys())
        # ...
        
        # Union of all dates
        all_dates = sorted(list(set().union(*[df.index for df in self.data.values()])))
        
        # Calculate Signals per ticker
        all_signals = {}
        for ticker in tickers:
            ticker_data = self.data[ticker]
            all_signals[ticker] = self.strategy.generate_signals(ticker_data)
            
        # Iterating through time
        for date in all_dates:
            equity_from_positions = 0.0
            current_prices = {} 
            
            # 1. Update Prices & Calculate Equity first
            for ticker in tickers:
                price_series = self.data[ticker]['Close']
                if date in price_series.index and not np.isnan(price_series.loc[date]) and price_series.loc[date] > 1e-8:
                     price = price_series.loc[date]
                else:
                    historical = price_series.loc[:date]
                    historical = historical[historical > 1e-8]
                    if not historical.empty:
                        price = historical.iloc[-1]
                    else:
                        price = 0.0
                current_prices[ticker] = price
                if price > 0:
                    equity_from_positions += self.positions.get(ticker, 0) * price
            
            total_equity = self.cash + equity_from_positions
            
            # 2. Risk Checks
            self.peak_equity = max(self.peak_equity, total_equity)
            current_drawdown = (total_equity - self.peak_equity) / self.peak_equity
            
            can_trade = self.risk_manager.check_portfolio_health(current_drawdown)
            
            # 3. Execution Logic
            for ticker in tickers:
                current_price = current_prices[ticker]
                
                # ... Signal logic ...
                if date in all_signals[ticker].index:
                     signal_row = all_signals[ticker].loc[date]
                     target_position = signal_row['Signal']
                else:
                     target_position = -999 
                
                if current_price > 0 and target_position != -999:
                    current_qty = self.positions.get(ticker, 0)
                    
                    # Execution Price Logic
                    # If Latency is ON, we add slippage to the current_price before executing
                    execution_price = current_price
                    if self.use_latency:
                        # Assume 20% vol roughly for slippage calculation or calculate it
                        slippage = self.latency_model.simulate_slippage(current_price, volatility=0.20)
                        # Slippage is cost. If buying, price goes up. If selling, price goes down? 
                        # Actually simulate_slippage returned a price delta 'shock'. 
                        # In real markets, you cross spread + market moves away.
                        # We'll assume 'shock' is the random drift. 
                        # PLUS spread cost (e.g. 1bp)
                        
                        spread_cost = current_price * 0.0001
                        
                        if target_position == 1 and current_qty == 0: # Buying
                             # Buying: we pay Price + Spread + Shock (if shock against us)
                             # Let's simple add the absolute slippage magnitude as cost to be conservative
                             execution_price = current_price + spread_cost + abs(slippage)
                        elif target_position == 0 and current_qty > 0: # Selling
                             # Selling: we receive Price - Spread - Shock
                             execution_price = current_price - spread_cost - abs(slippage)
                    
                    
                    if target_position == 1 and current_qty == 0:
                        # Buy
                        if can_trade:
                            # Vol Sizing
                            try:
                                hist_start = date - pd.Timedelta(days=40)
                                subset = self.data[ticker].loc[hist_start:date]['Close'].pct_change().dropna()
                                if len(subset) > 10:
                                    asset_vol = subset.std() * np.sqrt(252)
                                else:
                                    asset_vol = 0.20
                            except:
                                asset_vol = 0.20
                            
                            allocation = self.risk_manager.get_allocation_amount(total_equity, asset_vol)
                            allocation = min(allocation, self.cash)
                            
                            if allocation > 0:
                                shares_to_buy = int(allocation // execution_price) # Use execution price
                                
                                if shares_to_buy > 0:
                                    cost = shares_to_buy * execution_price
                                    self.cash -= cost
                                    self.positions[ticker] = shares_to_buy

                    elif target_position == 0 and current_qty > 0:
                        # Sell
                        revenue = current_qty * execution_price # Use execution price
                        self.cash += revenue
                        self.positions[ticker] = 0
            
            # Recalculate generic portfolio value for the day
            # (Slightly redundant but clean)
            final_equity_positions = 0
            for ticker, price in current_prices.items():
                 final_equity_positions += self.positions.get(ticker, 0) * price
                 
            self.portfolio_value.append({'Date': date, 'PortfolioValue': self.cash + final_equity_positions})
            
        self.results = pd.DataFrame(self.portfolio_value).set_index('Date')
        self.results['Returns'] = self.results['PortfolioValue'].pct_change().fillna(0)
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        if not hasattr(self, 'results'):
            return {}
        return calculate_metrics(self.results['Returns'])
