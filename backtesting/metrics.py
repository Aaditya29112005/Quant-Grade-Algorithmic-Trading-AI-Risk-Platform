import numpy as np
import pandas as pd

def calculate_metrics(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> dict:
    """
    Calculates key performance metrics for a return series.
    
    Args:
        daily_returns: A pandas Series of daily returns (percentage change).
        risk_free_rate: Annualized risk-free rate (default 0.0).
        
    Returns:
        Dictionary containing Sharpe, Sortino, Max Drawdown, CAGR, Volatility.
    """
    # Annualization factor (assuming 252 trading days)
    N = 252
    
    mean_return = daily_returns.mean() * N
    volatility = daily_returns.std() * np.sqrt(N)
    
    # Sharpe Ratio
    if volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = (mean_return - risk_free_rate) / volatility
        
    # Sortino Ratio (Downside deviation only)
    negative_returns = daily_returns[daily_returns < 0]
    downside_std = negative_returns.std() * np.sqrt(N)
    if downside_std == 0:
        sortino_ratio = 0
    else:
        sortino_ratio = (mean_return - risk_free_rate) / downside_std
        
    # Max Drawdown
    cumulative_returns = (1 + daily_returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    
    # Total Return
    total_return = cumulative_returns.iloc[-1] - 1 if not cumulative_returns.empty else 0
    
    return {
        "Total Return": total_return,
        "Annualized Return": mean_return,
        "Annualized Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Max Drawdown": max_drawdown
    }
