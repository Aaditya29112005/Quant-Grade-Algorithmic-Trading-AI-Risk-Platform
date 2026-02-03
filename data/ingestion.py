import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict

class DataIngestion:
    """
    Handles fetching and processing of market data.
    """
    def __init__(self):
        pass

    def fetch_data(self, tickers: List[str], start_date: str, end_date: str, interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Fetches historical data for a list of tickers using yfinance.
        
        Args:
            tickers: List of ticker symbols (e.g., ['AAPL', 'MSFT'])
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval (default '1d')
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping ticker -> DataFrame with OHLCV columns.
        """
        print(f"Fetching data for {tickers} from {start_date} to {end_date}...")
        
        data_dict = {}
        
        # Download one by one to avoid MultiIndex complexity and ensure clean data frames
        # This is slightly slower but much safer for this roadmap phase.
        for ticker in tickers:
            try:
                # auto_adjust=True gives Open, High, Low, Close, Volume standard
                df = yf.download(ticker, start=start_date, end=end_date, interval=interval, auto_adjust=True, progress=False)
                if not df.empty:
                     # Flatten MultiIndex columns if present (Price, Ticker) -> (Price)
                     if isinstance(df.columns, pd.MultiIndex):
                         try:
                             # Try to drop the ticker level (usually level 1)
                             # Check if level 1 contains the ticker
                             if ticker in df.columns.get_level_values(1):
                                 df = df.xs(ticker, axis=1, level=1)
                         except Exception:
                             # Fallback: maybe just droplevel if size matches
                             if df.columns.nlevels > 1:
                                 df.columns = df.columns.droplevel(1)
                     
                     data_dict[ticker] = df
                else:
                    print(f"Warning: No data found for {ticker}")
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                
        return data_dict

    def get_ticker_data(self, data: Dict[str, pd.DataFrame], ticker: str) -> pd.DataFrame:
        """
        Helper to extract data for a specific ticker.
        """
        return data.get(ticker, pd.DataFrame())

