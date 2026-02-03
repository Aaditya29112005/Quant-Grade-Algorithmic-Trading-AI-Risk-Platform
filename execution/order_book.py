from dataclasses import dataclass
from typing import Literal

@dataclass
class LimitOrder:
    price: float
    quantity: int
    side: Literal['BUY', 'SELL']
    id: str

class OrderBook:
    """
    Simulates a simplified Limit Order Book.
    """
    def __init__(self):
        self.bids = [] # Buyers (Higher is better)
        self.asks = [] # Sellers (Lower is better)
        
    def get_market_price(self, mid_price: float, spread_bps: float = 5.0): # 5 bps spread
        """
        Simulates current Bid/Ask based on a mid-price and spread.
        """
        half_spread = spread_bps / 10000.0 / 2.0
        bid = mid_price * (1 - half_spread)
        ask = mid_price * (1 + half_spread)
        return bid, ask
    
    def check_execution(self, order: LimitOrder, market_data: dict) -> bool:
        """
        Determines if a limit order would execute given OHLCV for the period.
        """
        # Simplified: If order is BUY, and Low < Limit Price, it fills.
        # If order is SELL, and High > Limit Price, it fills.
        
        if order.side == 'BUY':
            # We want to buy at 'price' or lower.
            # Executed if market Low dropped below limit.
            if market_data['Low'] <= order.price:
                return True
        elif order.side == 'SELL':
            if market_data['High'] >= order.price:
                return True
                
        return False
