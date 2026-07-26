import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class MockDataGenerator:
    """
    Generates realistic market and financial statement data for testing.
    Supports TSMC (2330), MediaTek (2454), Evergreen (2603), Chunghwa Telecom (2412),
    AAPL, MSFT, and generic tickers.
    """
    
    TICKER_PROFILES = {
        "2330.TW": {"name": "台積電 (TSMC)", "sector": "Technology", "industry": "Semiconductors", "price": 950.0, "beta": 1.2, "volatility": 0.02, "trend": 0.0005},
        "2330": {"name": "台積電 (TSMC)", "sector": "Technology", "industry": "Semiconductors", "price": 950.0, "beta": 1.2, "volatility": 0.02, "trend": 0.0005},
        "2454.TW": {"name": "聯發科 (MediaTek)", "sector": "Technology", "industry": "Semiconductors", "price": 1200.0, "beta": 1.3, "volatility": 0.025, "trend": 0.0003},
        "2603.TW": {"name": "長榮海運 (Evergreen)", "sector": "Transportation", "industry": "Shipping", "price": 180.0, "beta": 1.5, "volatility": 0.035, "trend": 0.0001},
        "2412.TW": {"name": "中華電信 (Chunghwa Telecom)", "sector": "Utilities", "industry": "Telecommunications", "price": 120.0, "beta": 0.5, "volatility": 0.008, "trend": 0.0001},
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "price": 220.0, "beta": 1.1, "volatility": 0.015, "trend": 0.0006},
        "MSFT": {"name": "Microsoft Corp.", "sector": "Technology", "industry": "Software", "price": 420.0, "beta": 1.0, "volatility": 0.014, "trend": 0.0007},
    }

    @classmethod
    def get_profile(cls, ticker: str) -> dict:
        ticker_clean = ticker.upper()
        if ticker_clean in cls.TICKER_PROFILES:
            return cls.TICKER_PROFILES[ticker_clean]
        # Generic profile
        random.seed(hash(ticker_clean))
        sectors = ["Technology", "Financials", "Consumer", "Utilities", "Healthcare"]
        industries = {
            "Technology": ["Semiconductors", "Software", "Hardware"],
            "Financials": ["Banking", "Insurance"],
            "Consumer": ["Retail", "Automotive"],
            "Utilities": ["Power", "Telecommunications"],
            "Healthcare": ["Biotech", "Pharmaceuticals"]
        }
        sec = random.choice(sectors)
        ind = random.choice(industries[sec])
        return {
            "name": f"企業 {ticker_clean}",
            "sector": sec,
            "industry": ind,
            "price": random.uniform(50.0, 500.0),
            "beta": random.uniform(0.6, 1.6),
            "volatility": random.uniform(0.01, 0.03),
            "trend": random.uniform(-0.0002, 0.0008)
        }

    @classmethod
    def generate_price_history(cls, ticker: str, days: int = 1000) -> pd.DataFrame:
        profile = cls.get_profile(ticker)
        base_price = profile["price"]
        vol = profile["volatility"]
        trend = profile["trend"]
        
        # Set seed for repeatability based on ticker
        np.random.seed(abs(hash(ticker)) % (2**32))
        
        # Simulate log returns
        returns = np.random.normal(loc=trend, scale=vol, size=days)
        price_multipliers = np.exp(np.cumsum(returns))
        prices = base_price * (price_multipliers / price_multipliers[-1]) # Norm to ending price
        
        dates = [datetime.now() - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        df = pd.DataFrame({
            "Open": prices * (1 + np.random.normal(0, 0.005, days)),
            "High": prices * (1 + np.abs(np.random.normal(0.01, 0.005, days))),
            "Low": prices * (1 - np.abs(np.random.normal(0.01, 0.005, days))),
            "Close": prices,
            "Volume": np.random.randint(100000, 5000000, size=days)
        }, index=pd.to_datetime(dates))
        
        # Clean up High/Low
        df["High"] = df[["Open", "Close", "High"]].max(axis=1)
        df["Low"] = df[["Open", "Close", "Low"]].min(axis=1)
        
        return df

    @classmethod
    def generate_monthly_revenue(cls, ticker: str, months: int = 36) -> pd.DataFrame:
        profile = cls.get_profile(ticker)
        sector = profile["sector"]
        
        np.random.seed(abs(hash(ticker) + 1) % (2**32))
        
        # Base monthly revenue estimate (correlated with company size)
        base_rev = profile["price"] * 10000000 # scaling factor
        
        dates = [datetime.now() - timedelta(days=30 * i) for i in range(months)]
        dates.reverse()
        
        # Generate with seasonality
        revenues = []
        for i, dt in enumerate(dates):
            month = dt.month
            # Cyclical seasonality based on months (Q3-Q4 usually stronger)
            seasonality = 1.0 + 0.15 * np.sin(2 * np.pi * month / 12)
            # Add some random shock
            shock = np.random.normal(0, 0.05)
            # Trend growth
            growth = 1.0 + (i / 12) * (0.05 if sector == "Technology" else 0.02)
            
            val = base_rev * seasonality * growth * (1 + shock)
            revenues.append(val)
            
        df = pd.DataFrame({
            "Revenue": revenues
        }, index=pd.to_datetime(dates))
        
        # YoY calculation
        df["YoY"] = df["Revenue"].pct_change(12)
        return df

    @classmethod
    def generate_financial_statements(cls, ticker: str, quarters: int = 12) -> dict:
        profile = cls.get_profile(ticker)
        sector = profile["sector"]
        
        # Deterministic random seed
        random.seed(hash(ticker) + 2)
        np.random.seed(abs(hash(ticker) + 2) % (2**32))
        
        dates = []
        # Find the last standard reporting end dates (e.g. Dec 31, Sep 30, Jun 30, Mar 31)
        curr = datetime.now()
        q_end_month = ((curr.month - 1) // 3) * 3
        if q_end_month == 0:
            q_end_year = curr.year - 1
            q_end_month = 12
        else:
            q_end_year = curr.year
            
        dt = datetime(q_end_year, q_end_month, 30 if q_end_month in [6,9] else (31 if q_end_month in [3,12] else 31))
        for _ in range(quarters):
            dates.append(dt)
            # Step back 3 months
            m = dt.month - 3
            y = dt.year
            if m <= 0:
                m += 12
                y -= 1
            dt = datetime(y, m, 30 if m in [6,9] else (31 if m in [3,12] else 31))
        
        dates.reverse()
        
        # Financial profiles by sector
        # Technology: High margin, high cash, low debt, high ROE
        # Financials: Low gross margin, high assets/liabilities, high debt, stable ROE
        # Utilities: Medium margin, high fixed assets, high debt, stable cash flows, stable ROE
        # Transportation: Cyclical margins, high fixed assets, medium debt, highly volatile
        
        if sector == "Technology":
            g_margin, o_margin, n_margin = 0.52, 0.38, 0.32
            asset_turnover = 0.65
            debt_to_equity = 0.3
            inventory_pct = 0.08
        elif sector == "Financials":
            g_margin, o_margin, n_margin = 0.90, 0.25, 0.20 # Finance doesn't really have traditional COGS
            asset_turnover = 0.08
            debt_to_equity = 4.5
            inventory_pct = 0.00
        elif sector == "Utilities":
            g_margin, o_margin, n_margin = 0.30, 0.15, 0.12
            asset_turnover = 0.35
            debt_to_equity = 1.2
            inventory_pct = 0.02
        elif sector == "Transportation":
            g_margin, o_margin, n_margin = 0.25, 0.18, 0.14
            asset_turnover = 0.50
            debt_to_equity = 0.8
            inventory_pct = 0.01
        else: # Generic
            g_margin, o_margin, n_margin = 0.35, 0.15, 0.10
            asset_turnover = 0.50
            debt_to_equity = 0.6
            inventory_pct = 0.05
            
        base_quarter_rev = profile["price"] * 15000000
        
        income_statements = []
        balance_sheets = []
        cash_flows = []
        
        # Cumulative/Sequential growth simulation
        for i, dt in enumerate(dates):
            # Growth factor
            growth_factor = 1.0 + (i / 12) * (0.12 if sector == "Technology" else 0.04)
            seasonality = 1.0 + 0.10 * np.sin(2 * np.pi * dt.month / 12)
            noise = np.random.normal(0, 0.04)
            
            quarter_rev = base_quarter_rev * growth_factor * seasonality * (1 + noise)
            
            # Income Statement
            cogs = quarter_rev * (1 - g_margin + np.random.normal(0, 0.02))
            gp = quarter_rev - cogs
            opex = quarter_rev * (g_margin - o_margin + np.random.normal(0, 0.01))
            op_inc = gp - opex
            tax = op_inc * 0.20
            net_inc = op_inc - tax
            
            # Shares outstanding
            shares = 100000000 # 100M shares
            eps = net_inc / shares
            
            income_statements.append({
                "Date": dt.strftime("%Y-%m-%d"),
                "Total Revenue": quarter_rev,
                "Cost Of Revenue": cogs,
                "Gross Profit": gp,
                "Selling General Administrative": opex * 0.6,
                "Research Development": opex * 0.4 if sector == "Technology" else 0.0,
                "Operating Income": op_inc,
                "Tax Provision": tax,
                "Net Income": net_inc,
                "Basic EPS": eps
            })
            
            # Balance Sheet
            # Total Assets = Total Liabilities + Total Equity
            # Equity dynamic: grows by net income (with some dividend payout)
            base_equity = base_quarter_rev * 4 * (1.2 if sector == "Technology" else 0.8)
            equity = (base_equity + net_inc * 3) * growth_factor * (1 + np.random.normal(0, 0.02))
            liabilities = equity * (debt_to_equity + np.random.normal(0, 0.05))
            assets = equity + liabilities
            
            cash = assets * (0.25 if sector == "Technology" else 0.08)
            inventory = assets * inventory_pct
            current_assets = cash + inventory + assets * 0.15
            fixed_assets = assets - current_assets
            
            current_liabilities = liabilities * 0.5
            long_term_debt = liabilities * 0.5
            
            balance_sheets.append({
                "Date": dt.strftime("%Y-%m-%d"),
                "Total Assets": assets,
                "Current Assets": current_assets,
                "Cash Cash Equivalents And Short Term Investments": cash,
                "Inventory": inventory,
                "Gross PP&E": fixed_assets,
                "Total Liabilities Net Minority Interest": liabilities,
                "Current Liabilities": current_liabilities,
                "Long Term Debt": long_term_debt,
                "Stockholders Equity": equity
            })
            
            # Cash Flow Statement
            # Operating Cash Flow usually correlates with Net Income + Depreciation
            depreciation = fixed_assets * 0.025
            ocf = net_inc + depreciation + np.random.normal(0, o_margin * quarter_rev * 0.1)
            capex = depreciation * (1.8 if sector == "Technology" else 1.0) * (1 + np.random.normal(0, 0.1))
            fcf = ocf - capex
            
            cash_flows.append({
                "Date": dt.strftime("%Y-%m-%d"),
                "Operating Cash Flow": ocf,
                "Capital Expenditure": capex,
                "Free Cash Flow": fcf,
                "Net Income": net_inc
            })
            
        # Format as DataFrames like yfinance
        df_income = pd.DataFrame(income_statements).set_index("Date").T
        df_balance = pd.DataFrame(balance_sheets).set_index("Date").T
        df_cashflow = pd.DataFrame(cash_flows).set_index("Date").T
        
        return {
            "income": df_income,
            "balance": df_balance,
            "cashflow": df_cashflow,
            "info": {
                "sector": sector,
                "industry": profile["industry"],
                "longName": profile["name"],
                "shortName": profile["name"].split(" ")[0],
                "beta": profile["beta"],
                "trailingPE": profile["price"] / (float(df_income.loc["Basic EPS"].iloc[-4:].sum())),
                "priceToBook": profile["price"] / (float(df_balance.loc["Stockholders Equity"].iloc[-1]) / shares),
                "marketCap": profile["price"] * shares
            }
        }
