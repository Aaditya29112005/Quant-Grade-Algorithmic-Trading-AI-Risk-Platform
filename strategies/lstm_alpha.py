import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple
from strategies.base import Strategy
from ai.feature_engineering import FeatureEngineer

class LSTMModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 50, num_layers: int = 2, output_size: int = 1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return torch.sigmoid(out)

class LSTMAlphaStrategy(Strategy):
    def __init__(self, name: str = "LSTM_DeepAlpha", lookback_window: int = 60, training_window: int = 500):
        super().__init__(name)
        self.lookback_window = lookback_window
        self.training_window = training_window
        self.fe = FeatureEngineer()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def prepare_data(self, data: pd.DataFrame) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.fe.create_features(data).dropna()
        
        # Target: Next day return positive?
        features['Target'] = (features['Close'].shift(-1) > features['Close']).astype(int)
        features.dropna(inplace=True)
        
        feature_cols = [c for c in features.columns if c not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        X, y = [], []
        # Create sequences
        values = features[feature_cols].values
        targets = features['Target'].values
        
        for i in range(len(values) - self.lookback_window):
            X.append(values[i : i + self.lookback_window])
            y.append(targets[i + self.lookback_window])
            
        return torch.FloatTensor(np.array(X)), torch.FloatTensor(np.array(y).reshape(-1, 1)), features.index[self.lookback_window:]

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Simulates training and prediction.
        For a real backtest, this performs a single Train/Test split to verify alpha.
        """
        # Feature Engineering
        data_with_features = self.fe.create_features(data).dropna()
        
        if len(data_with_features) < self.training_window + self.lookback_window:
            return pd.DataFrame(index=data.index, columns=['Signal'], data=0)

        # Prepare Tensors
        feature_cols = [c for c in data_with_features.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']]
        # Normalize features
        df_norm = data_with_features[feature_cols].copy()
        df_norm = (df_norm - df_norm.mean()) / (df_norm.std() + 1e-8)
        
        # Re-attach target for splitting
        df_norm['Target'] = (data_with_features['Close'].shift(-1) > data_with_features['Close']).astype(int)
        df_norm.dropna(inplace=True)
        
        # Train/Test Split (70/30)
        split = int(len(df_norm) * 0.7)
        train_df = df_norm.iloc[:split]
        test_df = df_norm.iloc[split:]
        
        # Create Sequences (Helper for single batch)
        def create_sequences(df, lookback):
            X, y = [], []
            values = df[feature_cols].values
            targets = df['Target'].values
            for i in range(len(values) - lookback):
                X.append(values[i : i+lookback])
                y.append(targets[i+lookback])
            return torch.FloatTensor(np.array(X)).to(self.device), torch.FloatTensor(np.array(y).reshape(-1, 1)).to(self.device)

        X_train, y_train = create_sequences(train_df, self.lookback_window)
        X_test, _ = create_sequences(test_df, self.lookback_window)
        
        if len(X_train) == 0 or len(X_test) == 0:
             return pd.DataFrame(index=data.index, columns=['Signal'], data=0)

        # Initialize Model
        input_dim = X_train.shape[2]
        self.model = LSTMModel(input_dim).to(self.device)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Train
        epochs = 50 
        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self.model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            
        # Predict
        self.model.eval()
        with torch.no_grad():
            test_preds = self.model(X_test)
            
        # Convert to Signals
        # Align predictions with dates
        # The predictions correspond to the END of the sequence.
        # Test Data Start Index + Lookback
        test_dates = test_df.index[self.lookback_window:]
        
        pred_series = pd.Series(test_preds.cpu().numpy().flatten(), index=test_dates)
        
        signals = pd.DataFrame(index=data.index)
        signals['Signal'] = 0
        
        # Threshold 0.5
        buy_signals = pred_series[pred_series > 0.55].index # Conviction
        sell_signals = pred_series[pred_series < 0.45].index
        
        signals.loc[buy_signals, 'Signal'] = 1
        signals.loc[sell_signals, 'Signal'] = 0 # Sell/Cash inputs
        
        return signals
