import numpy as np
import pandas as pd

class VolatilitySizing:
    def __init__(self, target_volatility: float = 0.20):
        """
        Args:
            target_volatility: Annualized target volatility (e.g., 0.20 for 20%).
        """
        self.target_volatility = target_volatility

    def get_position_size(self, current_volatility: float, capital: float) -> float:
        """
        Calculates position size (in dollars) to achieve target volatility.
        Formula: Size = (TargetVol / AssetVol) * Capital
        
        Args:
            current_volatility: Annualized asset volatility (e.g., 0.30).
            capital: Available capital.
            
        Returns:
            Dollar amount to allocate.
        """
        if current_volatility <= 0:
            return 0.0
        
        # Cap leverage at 1.0 (or some limit) to prevent blowing up on low vol
        leverage = self.target_volatility / current_volatility
        leverage = min(leverage, 1.0) # Conservative: max 100% allocation
        
        return capital * leverage
