import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture

class RegimeDetector:
    """
    Detects market regimes (e.g., Low Volatility vs High Volatility) using Unsupervised Learning.
    """
    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        self.model = GaussianMixture(n_components=n_components, covariance_type="full", random_state=42)
        
    def fit_predict(self, returns: pd.Series) -> pd.Series:
        """
        Fits GMM on returns/volatility and predicts regime for each timestamp.
        
        Args:
            returns: Series of log returns.
            
        Returns:
            Series of regime labels (0, 1, ...).
        """
        # Feature for regime detection: usually Volatility is the best discriminator
        # We model the distribution of returns or rolling volatility.
        # Let's use Returns and Rolling Volatility combined.
        
        data = pd.DataFrame(index=returns.index)
        data['Returns'] = returns
        data['Vol_10'] = returns.rolling(window=10).std()
        data.dropna(inplace=True)
        
        if data.empty:
            return pd.Series(0, index=returns.index)
            
        X = data[['Returns', 'Vol_10']].values
        
        self.model.fit(X)
        regimes = self.model.predict(X)
        
        # Align labels so that higher volatility regime is always the same label (heuristically)
        # We can analyze the means/variances of clusters later. For now, just return raw labels.
        
        # Re-index to match original returns (pad beginning with 0 or NaN)
        result = pd.Series(index=data.index, data=regimes)
        
        # We return the serie reindexed to original to handle the dropna
        return result.reindex(returns.index).bfill().fillna(0)
