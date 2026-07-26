"""
System-wide configuration settings for StockVision Pro.
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Cache settings
CACHE_DB_PATH = os.path.join(DATA_DIR, "cache.db")
CACHE_MAX_AGE_DAYS = 1.0

# Valuation & DCF Defaults
DEFAULT_RISK_FREE_RATE = 0.03 # 3%
DEFAULT_EQUITY_RISK_PREMIUM = 0.06 # 6%
MIN_WACC = 0.07 # 7%
MAX_WACC = 0.12 # 12%
TERMINAL_GROWTH_RATE = 0.02 # 2%

# Backtest Settings
BACKTEST_MIN_DAYS = 100
BACKTEST_STEP_DAYS = 20 # Evaluate signal every ~20 trading days (monthly)

# Server Config
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
