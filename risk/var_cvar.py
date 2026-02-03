import numpy as np
import pandas as pd

class RiskMetrics:
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculates Historical Value at Risk (VaR).
        
        Args:
            returns: Series of returns.
            confidence_level: (e.g., 0.95).
            
        Returns:
            VaR value (positive float representing loss %).
        """
        if returns.empty:
            return 0.0
            
        # VaR is the quantile of the loss distribution
        # e.g., 0.95 confidence -> 5th percentile worst return
        percentile = (1 - confidence_level) * 100
        var_value = np.percentile(returns, percentile)
        
        # Return as positive percentage loss hint
        return -var_value

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculates Conditional Value at Risk (CVaR) / Expected Shortfall.
        """
        if returns.empty:
            return 0.0
            
        percentile = (1 - confidence_level) * 100
        var_threshold = np.percentile(returns, percentile)
        
        # Average of returns worse than VaR
        shortfall = returns[returns <= var_threshold].mean()
        
        return -shortfall
