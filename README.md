# 💹 Innovation — Forex Trading Simulator

![Simulator Screenshot](https://github.com/Es-Kiani/Innovation/blob/main/Img/Screenshot%202025-04-18%20215238.png)

## 🚀 Overview

**Innovation** is a powerful and interactive **Forex Trading Simulator** built for learners, analysts, and AI developers who want to experience the real feel of trading without risking capital. It brings you a feature-rich environment for backtesting strategies, observing market behavior, and training AI models in a controlled setup.

Whether you're a beginner learning how to trade, a developer building automated trading agents, or an expert validating strategies — **Innovation** has you covered!

---

## 🌟 Key Features

### 📊 Core Simulation
- Realistic simulation of **AUD/CAD** price action using historical candle data
- Play, pause, forward, and backward navigation through market candles
- **Line and candlestick charts** with multi-indicator overlays

### 📈 Indicators (Optional)
- SMA20 / SMA50 / SMA200
- RSI (14) and MACD overlays
- Toggle indicators from menu dynamically

### 🧮 Trading Environment
- Open/Close Buy & Sell trades with leverage, stop-loss, and risk %
- Virtual account balance tracking and trade size calculation
- Support for AI-driven trades (via API)

### 📑 Trade Management
- Detailed **open trades table** with real-time P&L calculation
- Historical trade chart view with entry/exit markers
- Trade list with profit logs and timestamps

### 🖥️ Chart Control & Data Display
- Toggle chart visibility to reduce clutter
- Even when the chart is hidden:
  - See **live OHLC** (Open, High, Low, Close) prices of the current candle
  - With trend emoji indicators:
    - 📈 for bullish
    - 📉 for bearish
    - ➖ for neutral

### ⏱️ Dynamic Speed Control
- **Logarithmic speed slider** for smooth fast/slow playback
- **Manual speed input** (in ms) for fine control

---

## 🎯 Use Cases

- 🧪 Backtesting trading strategies without real money
- 📚 Teaching and learning the concepts of market orders and risk
- 🤖 Developing and testing AI models in a synthetic trading loop
- 🔁 Replaying past market scenarios with precision control

---

## 🛠️ Tech Stack

| Component       | Technology                  |
|----------------|-----------------------------|
| Language        | Python                      |
| UI Framework    | PyQt5                       |
| Charting        | Matplotlib + mpl_finance    |
| Data Handling   | Pandas                      |
| Backend API     | Flask                       |

---

## ▶️ How to Run

### 🔁 Clone the Repo

```bash
git clone https://github.com/Es-Kiani/Innovation.git
cd Innovation
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

> *(If you don’t have it yet, install PyQt5: `pip install PyQt5 matplotlib pandas flask`)*

### 🧠 Load Your Dataset

Ensure your CSV is configured correctly. By default:
```python
# DEFINEs.py
DATASET_FILE_PATH = "D:/Innovation/Dataset/AUDCAD_Dataset.csv"
```

Update the path if needed.

### 🚦 Run the Simulator

```bash
python main.py
```

---

## 🔮 Future Plans

- Real-time market data integration (via broker API)
- Mobile-friendly UI with touch controls
- AI strategy tester & benchmark mode
- Leaderboard & multiplayer trading challenges

---

## 🤝 Contributing

We welcome your contributions! 🛠  
To help improve the simulator, feel free to:

- Report bugs
- Suggest features
- Submit pull requests

---

## 📅 Last Updated

**April 18, 2025**

---

Made with ❤️ for learning, experimentation, and innovation.
