import pandas as pd
import numpy as np
from utils.helper import safe_divide, clamp

class TechnicalAnalyzer:
    """
    Analyzes price action, moving averages, and technical indicators.
    """
    def __init__(self, processed_data: dict):
        self.ticker = processed_data.get("ticker", "")
        self.df_daily = pd.DataFrame(processed_data.get("daily_data", []))

    def analyze(self) -> dict:
        """
        Extract technical features. Returns a dictionary of features.
        """
        features = {}
        
        if self.df_daily.empty or len(self.df_daily) < 14 or "Close" not in self.df_daily.columns:
            features.update({
                "rsi": 50.0,
                "macd_hist": 0.0,
                "distance_ma50": 0.0,
                "distance_ma200": 0.0,
                "ma_alignment": 0.5,
                "volatility": 0.20
            })
            return features
            
        close = self.df_daily["Close"].astype(float)
        
        # 1. RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Safe RSI computation
        last_gain = gain.iloc[-1] if not pd.isna(gain.iloc[-1]) else 0.0
        last_loss = loss.iloc[-1] if not pd.isna(loss.iloc[-1]) else 0.0
        if last_loss == 0:
            rsi_val = 100.0 if last_gain > 0 else 50.0
        else:
            rs = last_gain / last_loss
            rsi_val = 100.0 - (100.0 / (1.0 + rs))
        features["rsi"] = clamp(float(rsi_val), 0.0, 100.0)

        # 2. MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        latest_hist = hist.iloc[-1] if not pd.isna(hist.iloc[-1]) else 0.0
        latest_close = close.iloc[-1] if not pd.isna(close.iloc[-1]) else 1.0
        features["macd_hist"] = safe_divide(latest_hist, latest_close, default=0.0)

        # 3. Moving Averages
        ma20 = close.rolling(window=20).mean()
        ma50 = close.rolling(window=50).mean()
        ma200 = close.rolling(window=200).mean() if len(close) >= 200 else close.rolling(window=min(len(close), 50)).mean()
        
        latest_ma20 = ma20.iloc[-1] if not pd.isna(ma20.iloc[-1]) else latest_close
        latest_ma50 = ma50.iloc[-1] if not pd.isna(ma50.iloc[-1]) else latest_close
        latest_ma200 = ma200.iloc[-1] if not pd.isna(ma200.iloc[-1]) else latest_close
        
        features["distance_ma50"] = safe_divide(latest_close - latest_ma50, latest_ma50, default=0.0)
        features["distance_ma200"] = safe_divide(latest_close - latest_ma200, latest_ma200, default=0.0)
        
        # 4. MA Alignment (Long-term Bull vs Bear)
        score = 0.0
        if latest_close > latest_ma20: score += 0.25
        if latest_ma20 > latest_ma50: score += 0.25
        if latest_ma50 > latest_ma200: score += 0.25
        if latest_close > latest_ma200: score += 0.25
        features["ma_alignment"] = score

        # 5. Volatility (Annualized 30-day volatility of daily returns)
        returns = close.pct_change()
        vol30 = returns.rolling(window=30).std()
        latest_vol = vol30.iloc[-1]
        features["volatility"] = float(latest_vol * np.sqrt(252)) if not pd.isna(latest_vol) else 0.20
        
        return features
