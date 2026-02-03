# Quant-Grade AI Algorithmic Trading Platform 🤖📈

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

An institutional-grade algorithmic trading platform featuring **Machine Learning Alpha**, **Market Regime Detection**, **Volatility Targeting**, and **Latency Simulation**.

Designed for researchers and quants to backtest strategies with realistic market microstructure constraints.

---

## 🏗 System Architecture

```mermaid
graph TD
    Data[Data Ingestion (yfinance)] --> Features[Feature Engineering]
    Features --> AI[AI Layer]
    
    subgraph "AI Core"
        AI --> Regime[Regime Detection (GMM)]
        AI --> Alpha[Alpha Model (Random Forest)]
    end
    
    Alpha --> Strategy[Strategy Logic]
    Regime --> Strategy
    
    Strategy --> Engine[Backtest Engine]
    
    subgraph "Risk & Execution"
        Engine --> Risk[Risk Manager (Vol Target + VaR)]
        Engine --> Exec[Execution (Latency + Slippage)]
    end
    
    Engine --> Dashboard[Streamlit Dashboard]
```

## 🚀 Key Features

### 1. Alpha Generation 🧠
-   **Machine Learning**: `RandomForestClassifier` predicting directional moves.
-   **Regime Detection**: `GaussianMixture` models identifying "High Volatility" vs "Low Volatility" states.
-   **Feature Engineering**: Lagged returns, volatility, RSI, SMA distances.

### 2. Risk Management 🛡️
-   **Volatility Targeting**: Dynamically adjusts position size inversely to asset volatility (Target: 20% Ann. Vol).
-   **Kill Switch**: Automatically halts trading if Max Drawdown exceeds 25%.
-   **VaR & CVaR**: Real-time calculation of Value at Risk.

### 3. Execution with Microstructure 📉
-   **Latency Simulation**: Models delay between Signal and Execution (e.g., 100ms).
-   **Slippage Model**: Simulates cost impact based on volatility and latency.
-   **Order Book**: Basic Limit Order logic.

### 4. Interactive Dashboard 📊
-   Built with **Streamlit** & **Plotly**.
-   Visualize Equity Curves, Underwater Plots (Drawdowns), and Trade Logs.
-   Run simulations on-the-fly.

---

## 🛠 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Aaditya29112005/Quant-Grade-Algorithmic-Trading-AI-Risk-Platform.git
    cd quant-platform
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃 Usage

### 1. Run the Dashboard (Recommended)
The easiest way to explore the platform is via the web UI.
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your browser.

### 2. Run Verification Scripts
Test individual components via the CLI:
```bash
# Test ML Alpha & Regime Detection
python tests/check_phase4.py

# Test Risk Management (Vol Targeting)
python tests/check_phase5.py

# Test Execution Latency
python tests/check_phase6.py
```

---

## 📂 Project Structure

```
quant-platform/
├── ai/                 # AI Models (Features, Regime, Alpha)
├── backtesting/        # Event-driven Backtest Engine
├── data/               # Data Ingestion (yfinance)
├── dashboard/          # Streamlit Web App
├── execution/          # Latency & Order Book Models
├── risk/               # Risk Management (VaR, Sizing)
├── strategies/         # Strategy Logic (Momentum, ML)
├── tests/              # Verification Scripts
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## 📜 License
MIT License.
