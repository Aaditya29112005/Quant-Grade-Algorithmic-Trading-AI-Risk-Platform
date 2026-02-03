import numpy as np
import pandas as pd

class LatencyModel:
    def __init__(self, mean_latency_ms: float = 100.0, std_latency_ms: float = 20.0):
        """
        Simulates execution latency.
        
        Args:
            mean_latency_ms: Average delay in milliseconds.
            std_latency_ms: Standard deviation of delay.
        """
        self.mean_latency = mean_latency_ms
        self.std_latency = std_latency_ms
        
    def get_latency(self) -> float:
        """Returns a random latency in milliseconds."""
        return max(0, np.random.normal(self.mean_latency, self.std_latency))
    
    def simulate_slippage(self, current_price: float, volatility: float, volume: float = 1.0) -> float:
        """
        Estimates price slippage based on volatility and latency.
        Simple model: Higher volatility + latency = larger potential slippage.
        
        Args:
            current_price: Asset price.
            volatility: Annualized volatility (scaling factor).
            volume: Trade size (impact model - placeholder).
            
        Returns:
            Executed price (adjusted for slippage).
        """
        # Time-based slippage: Price moves during latency
        # approximated by random walk drift proportional to volatility
        
        # 100ms latency as fraction of trading day (6.5 hours)
        # 6.5 * 3600 * 1000 = 23,400,000 ms
        ms_per_day = 23400000
        latency_ms = self.get_latency()
        
        time_fraction = latency_ms / ms_per_day
        
        # Expected move ~ Vol * Price * sqrt(t)
        # Random shock +/-
        shock = np.random.normal(0, 1) * volatility * current_price * np.sqrt(time_fraction)
        
        # Bid-Ask spread impact (fixed cost approximation + shock)
        # Assume 1bp fixed spread cost + shock
        spread_cost = current_price * 0.0001
        
        # If buying, we pay more (add cost, add/sub shock)
        # But this method returns "executed price" generic deviation.
        # We'll assume this wraps the 'execution price' logic.
        
        # Let's return the Price Delta
        return shock
