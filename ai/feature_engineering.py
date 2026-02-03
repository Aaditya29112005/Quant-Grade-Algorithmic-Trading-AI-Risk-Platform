import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Generates technical indicators and features for Machine Learning models.
    """
    def __init__(self):
        pass
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Adds technical features to the Open-High-Low-Close-Volume data.
        
        Args:
            data: DataFrame with columns 'Open', 'High', 'Low', 'Close', 'Volume'.
            
        Returns:
            DataFrame with added feature columns, NaN rows dropped.
        """
        df = data.copy()
        
        # 1. Returns and Lags
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        for lag in [1, 2, 3, 5]:
            df[f'Lag_{lag}'] = df['Log_Returns'].shift(lag)
            
        # 2. Volatility (Rolling Std Dev)
        df['Vol_5'] = df['Log_Returns'].rolling(window=5).std()
        df['Vol_20'] = df['Log_Returns'].rolling(window=20).std()
        
        # 3. Simple Moving Averages & Distances
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['Dist_SMA_10'] = (df['Close'] - df['SMA_10']) / df['SMA_10']
        df['Dist_SMA_50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        
        # 4. Momentum (RSI Approximation)
        # Using simple RSI calculation since ta-lib is not available
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 5. Volume Changes
        df['Vol_Change'] = df['Volume'].pct_change()
        
        # Drop NaNs created by lags/rolling
        df.dropna(inplace=True)
        
        return df
