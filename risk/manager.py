from risk.position_sizing import VolatilitySizing

class RiskManager:
    def __init__(self, target_volatility: float = 0.20, max_drawdown_limit: float = 0.20):
        self.vol_sizer = VolatilitySizing(target_volatility)
        self.max_drawdown_limit = max_drawdown_limit
        self.kill_switch_active = False

    def check_portfolio_health(self, current_drawdown: float) -> bool:
        """
        Checks if kill switch should be activated.
        """
        if current_drawdown < -self.max_drawdown_limit:
            self.kill_switch_active = True
            print(f"RISK ALERT: Max Drawdown Limit Hit ({current_drawdown:.2%}). Stopping Trading.")
            return False # Unhealthy
        return True # Healthy

    def get_allocation_amount(self, capital: float, asset_volatility: float) -> float:
        """
        Determines dollar amount to allocate based on volatility targeting.
        """
        if self.kill_switch_active:
            return 0.0
            
        return self.vol_sizer.get_position_size(asset_volatility, capital)
