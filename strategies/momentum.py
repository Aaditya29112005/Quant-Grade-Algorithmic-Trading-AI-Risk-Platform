from strategies.base import Strategy
import pandas as pd
import numpy as np

class MomentumStrategy(Strategy):
    """
    A simple Momentum strategy based on Moving Average Crossover.
    Buy when Short Window SMA crosses above Long Window SMA.
    Sell when Short Window SMA crosses below Long Window SMA.
    """
    def __init__(self, short_window: int = 50, long_window: int = 200):
        super().__init__(name="Momentum_SMAvLMA")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates signals for a given ticker's data.
        """
        signals = pd.DataFrame(index=data.index)
        signals['Signal'] = 0.0
        
        # Calculate Short and Long SMAs
        signals['Short_MA'] = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['Long_MA'] = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Generate Signal: 1 if Short > Long, 0 otherwise (for now effectively long-only or flattened)
        # To make it a proper signal generation:
        # 1 = Long, -1 = Short, 0 = Cash
        signals['Signal'] = np.where(signals['Short_MA'] > signals['Long_MA'], 1.0, 0.0)
        
        # Generate Limit Orders / Positions
        # signal logic: Position is 1 if Short > Long.
        # We take the difference to find the crossover points (trades)
        signals['Positions'] = signals['Signal'].diff()
        
        return signals
