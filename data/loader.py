import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.cache import LocalCache
from data.mock_generator import MockDataGenerator
from config import CACHE_MAX_AGE_DAYS

class DataLoader:
    def __init__(self):
        self.cache = LocalCache()

    def clean_ticker(self, ticker: str) -> str:
        """
        Standardizes ticker. For numerical Taiwanese tickers, append .TW.
        """
        ticker = ticker.strip().upper()
        if ticker.isdigit():
            return f"{ticker}.TW"
        return ticker

    def get_data(self, ticker: str, force_refresh: bool = False) -> dict:
        """
        Load price history, financials, monthly revenue, and info.
        Checks cache first.
        """
        ticker = self.clean_ticker(ticker)
        cache_key = f"{ticker}:all_data"
        
        if not force_refresh:
            cached = self.cache.get(cache_key, max_age_days=CACHE_MAX_AGE_DAYS)
            if cached:
                print(f"[{ticker}] Loaded data from cache.")
                return cached

        print(f"[{ticker}] Fetching real-time data...")
        data = None
        try:
            data = self._fetch_real_data(ticker)
        except Exception as e:
            print(f"[{ticker}] Error fetching real data: {e}. Falling back to mock data.")
            
        if not data:
            # Generate mock data
            print(f"[{ticker}] Generating mock data...")
            mock_financials = MockDataGenerator.generate_financial_statements(ticker)
            mock_price = MockDataGenerator.generate_price_history(ticker)
            mock_revenue = MockDataGenerator.generate_monthly_revenue(ticker)
            
            df_price = mock_price.reset_index().rename(columns={"index": "Date"})
            df_price["Date"] = pd.to_datetime(df_price["Date"]).dt.strftime("%Y-%m-%d")
            
            df_revenue = mock_revenue.reset_index().rename(columns={"index": "Date"})
            df_revenue["Date"] = pd.to_datetime(df_revenue["Date"]).dt.strftime("%Y-%m-%d")
            
            data = {
                "ticker": ticker,
                "price": df_price.to_dict(orient="records"),
                "revenue": df_revenue.to_dict(orient="records"),
                "financials": {
                    "income": mock_financials["income"].to_dict(),
                    "balance": mock_financials["balance"].to_dict(),
                    "cashflow": mock_financials["cashflow"].to_dict(),
                    "info": mock_financials["info"]
                },
                "source": "mock",
                "timestamp": datetime.now().isoformat()
            }
        
        # Save to cache
        self.cache.set(cache_key, data)
        return data

    def _fetch_real_data(self, ticker: str) -> dict:
        """
        Fetches real stock data using yfinance and finmind.
        """
        yf_ticker = yf.Ticker(ticker)
        
        # 1. Fetch Price History (3 years)
        hist = yf_ticker.history(period="3y")
        if hist.empty:
            raise ValueError(f"No price history found for {ticker}")
            
        df_price = hist.reset_index()
        # Handle datetime index / column
        date_col = "Date" if "Date" in df_price.columns else df_price.columns[0]
        df_price["Date"] = pd.to_datetime(df_price[date_col]).dt.strftime("%Y-%m-%d")
        
        # 2. Fetch Info
        info = {}
        try:
            info = yf_ticker.info or {}
        except Exception:
            pass
            
        ticker_profile = MockDataGenerator.get_profile(ticker)
        cleaned_info = {
            "sector": info.get("sector") or ticker_profile["sector"],
            "industry": info.get("industry") or ticker_profile["industry"],
            "longName": info.get("longName") or info.get("shortName") or ticker_profile["name"],
            "shortName": info.get("shortName") or ticker_profile["name"].split(" ")[0],
            "beta": float(info.get("beta") or ticker_profile["beta"]),
            "trailingPE": float(info.get("trailingPE") or info.get("forwardPE") or 15.0),
            "priceToBook": float(info.get("priceToBook") or 1.5),
            "marketCap": float(info.get("marketCap") or 10000000000)
        }
        
        # 3. Fetch Financial Statements
        income = yf_ticker.quarterly_financials
        balance = yf_ticker.quarterly_balance_sheet
        cashflow = yf_ticker.quarterly_cashflow
        
        if income is None or income.empty:
            income = yf_ticker.financials
        if balance is None or balance.empty:
            balance = yf_ticker.balance_sheet
        if cashflow is None or cashflow.empty:
            cashflow = yf_ticker.cashflow
            
        if income is None or income.empty or balance is None or balance.empty or cashflow is None or cashflow.empty:
            raise ValueError("Fundamental financial data is incomplete")
            
        # Convert columns to string format %Y-%m-%d
        for df_stmt in [income, balance, cashflow]:
            df_stmt.columns = [
                c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c)[:10] 
                for c in df_stmt.columns
            ]
        
        financials = {
            "income": income.to_dict(),
            "balance": balance.to_dict(),
            "cashflow": cashflow.to_dict(),
            "info": cleaned_info
        }
        
        # 4. Fetch Monthly Revenue
        df_rev = pd.DataFrame()
        is_taiwan = ticker.endswith(".TW") or ticker.endswith(".TWO")
        
        if is_taiwan:
            try:
                stock_id = ticker.split(".")[0]
                from FinMind.data import DataLoader as FM_DataLoader
                fm = FM_DataLoader()
                start_date = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")
                fm_df = fm.taiwan_stock_month_revenue(stock_id=stock_id, start_date=start_date)
                if fm_df is not None and not fm_df.empty:
                    df_rev = fm_df[["date", "revenue"]].rename(columns={"date": "Date", "revenue": "Revenue"})
                    df_rev["Date"] = pd.to_datetime(df_rev["Date"]).dt.strftime("%Y-%m-%d")
                    df_rev = df_rev.sort_values("Date").reset_index(drop=True)
                    df_rev["YoY"] = df_rev["Revenue"].pct_change(12)
            except Exception as fe:
                print(f"[{ticker}] FinMind fetch failed: {fe}. Resampling from quarterly revenue.")
                
        if df_rev.empty:
            dates = sorted(list(income.columns))
            rev_series = []
            for d in dates:
                rev = income.loc["Total Revenue", d] if "Total Revenue" in income.index else None
                if pd.isna(rev) or rev is None:
                    rev = income.loc["Revenue", d] if "Revenue" in income.index else None
                if rev is not None and not pd.isna(rev):
                    rev_series.append((d, float(rev)))
            
            if rev_series:
                rev_series = sorted(rev_series, key=lambda x: x[0])
                monthly_records = []
                for idx, (date_str, q_rev) in enumerate(rev_series):
                    try:
                        q_dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                        m_rev = q_rev / 3.0
                        for m_offset in range(3):
                            m_dt = q_dt - timedelta(days=30 * m_offset)
                            monthly_records.append({
                                "Date": m_dt.strftime("%Y-%m-%d"),
                                "Revenue": m_rev
                            })
                    except Exception:
                        continue
                if monthly_records:
                    df_rev = pd.DataFrame(monthly_records).sort_values("Date").drop_duplicates(subset=["Date"])
                    df_rev = df_rev.reset_index(drop=True)
                    df_rev["YoY"] = df_rev["Revenue"].pct_change(12)
                    
        if df_rev.empty:
            df_rev = MockDataGenerator.generate_monthly_revenue(ticker).reset_index().rename(columns={"index": "Date"})
            df_rev["Date"] = pd.to_datetime(df_rev["Date"]).dt.strftime("%Y-%m-%d")
            df_rev["YoY"] = df_rev["Revenue"].pct_change(12) if "Revenue" in df_rev.columns else 0.0
                
        price_records = df_price[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")
        rev_records = df_rev[["Date", "Revenue", "YoY"]].to_dict(orient="records") if not df_rev.empty else []
        
        return {
            "ticker": ticker,
            "price": price_records,
            "revenue": rev_records,
            "financials": financials,
            "source": "real",
            "timestamp": datetime.now().isoformat()
        }

    def get_price(self, ticker: str):
        return self.get_data(ticker)["price"]

    def get_monthly_revenue(self, ticker: str):
        return self.get_data(ticker)["revenue"]

    def get_financial_statement(self, ticker: str):
        return self.get_data(ticker)["financials"]