from strategies.base import Strategy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ai.feature_engineering import FeatureEngineer

class MLAlphaStrategy(Strategy):
    """
    Machine Learning based Alpha Strategy.
    Uses Random Forest to predict next day's return direction.
    """
    def __init__(self, train_window: int = 252):
        super().__init__(name="ML_RandomForest_Alpha")
        self.train_window = train_window # Rolling train window or initial batch size
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.fe = FeatureEngineer()
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates buy/sell signals based on ML predictions.
        Note: In a real HFT/Live engine, we retrain periodically. 
        Here, for simplicity of the backtest loop, we will do a single 'Split' or a 'Walk-Forward' simulation?
        
        To fit into the current 'generate_signals' returning a full DataFrame at once:
        We will simulate a Walk-Forward measurement:
        1. Use initial 'train_window' to train.
        2. Predict next day. 
        3. Simple approach: Train once on first X% (e.g. 50%) data, test on rest.
           This avoids retraining 1000 times in loop which is slow for python.
        """
        
        # 1. Feature Engineering
        df_features = self.fe.create_features(data)
        
        # Target: 1 if Next Close > Current Close, else 0
        df_features['Target'] = np.where(df_features['Close'].shift(-1) > df_features['Close'], 1, 0)
        
        # Drop last row as it has no target
        df_model = df_features.dropna()
        
        # Define Split
        split_point = int(len(df_model) * 0.7) # Train on first 70%
        
        train_data = df_model.iloc[:split_point]
        test_data = df_model.iloc[split_point:]
        
        if train_data.empty or test_data.empty:
            print("Not enough data for ML split.")
            signals = pd.DataFrame(index=data.index)
            signals['Signal'] = 0.0
            signals['Positions'] = 0.0
            return signals

        feature_cols = [c for c in df_model.columns if c not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
        
        X_train = train_data[feature_cols]
        y_train = train_data['Target']
        
        X_test = test_data[feature_cols]
        # y_test = test_data['Target']
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Predict on Test (and Train for visualization, though biased)
        # We only generate signals for the test period to avoid look-ahead bias in the "backtest" results
        # The backtester will run through all dates, but our signal will differ.
        
        # Generate predictions for the WHOLE dataset (features) to align indices, 
        # but mock the signals as 0 for the training period to simulate "waiting to train".
        
        all_X = df_model[feature_cols]
        predictions = self.model.predict(all_X)
        
        # Create Signals DataFrame aligned with ORIGINAL data index
        signals = pd.DataFrame(index=data.index)
        signals['Signal'] = 0.0
        
        # Map predictions back. 
        # CAUTION: df_model has dropped rows (features).
        # We place predictions at the corresponding indices.
        
        pred_series = pd.Series(predictions, index=df_model.index)
        
        # Only keep signals for the test period (after split point)
        test_start_date = test_data.index[0]
        
        # Logic: If pred=1 -> Buy (Signal 1). If pred=0 -> Cash/Neutra (Signal 0)
        # Or Short? Let's stick to Long/Cash for now.
        
        signals.loc[df_model.index, 'Signal_Raw'] = pred_series
        
        # Filter: Set Signal to 0 before test_start_date
        signals.loc[:test_start_date, 'Signal'] = 0.0
        signals.loc[test_start_date:, 'Signal'] = signals.loc[test_start_date:, 'Signal_Raw']
        
        # Calculate Positions (Change)
        signals['Positions'] = signals['Signal'].diff()
        
        return signals
