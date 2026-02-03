from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """
    Abstract Base Class for all trading strategies.
    Ensures a consistent interface for the BacktestEngine.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates trading signals based on the provided data.
        
        Args:
            data: DataFrame containing market data (Open, High, Low, Close, Volume).
            
        Returns:
            DataFrame with the same index as input, containing a 'Signal' column.
            Signal values: 1 (Buy), -1 (Sell), 0 (Hold/Neutral).
        """
        pass
