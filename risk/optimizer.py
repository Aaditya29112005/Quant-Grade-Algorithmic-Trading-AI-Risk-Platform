import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List

class PortfolioOptimizer:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_mean_variance_weights(self, prices: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates Tangency Portfolio weights (Max Sharpe Ratio).
        """
        returns = prices.pct_change().dropna()
        if returns.empty:
            return {col: 1.0/len(prices.columns) for col in prices.columns}

        mu = returns.mean() * 252
        cov = returns.cov() * 252
        n_assets = len(returns.columns)
        
        # Objective: Minimize Negative Sharpe
        def negative_sharpe(weights):
            p_ret = np.dot(weights, mu)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            return -(p_ret - self.risk_free_rate) / p_vol
        
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        init_guess = n_assets * [1. / n_assets]
        
        result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return dict(zip(prices.columns, result.x))

    def calculate_risk_parity_weights(self, prices: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates Risk Parity weights (Inverse Volatility / Equal Risk Contribution).
        Simplified version: Inverse Volatility.
        """
        returns = prices.pct_change().dropna()
        vol = returns.std()
        
        inv_vol = 1.0 / vol
        weights = inv_vol / inv_vol.sum()
        
        return weights.to_dict()
