import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    """
    Standardizes financial data keys and aligns quarterly statements with daily price data.
    """

    # Mapping of standard keys to possible yfinance keys
    KEY_MAPPINGS = {
        "revenue": ["Total Revenue", "Revenue", "Operating Revenue"],
        "gross_profit": ["Gross Profit"],
        "operating_income": ["Operating Income", "Operating Income Value"],
        "net_income": ["Net Income", "Net Income Common Stockholders", "Net Income Loss", "Net Income Including Noncontrolling Interests"],
        "eps": ["Basic EPS", "Diluted EPS", "BasicAverageShares"],
        "assets": ["Total Assets", "Total Assets Value"],
        "liabilities": ["Total Liabilities Net Minority Interest", "Total Liabilities"],
        "equity": ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"],
        "current_assets": ["Current Assets", "Total Current Assets"],
        "current_liabilities": ["Current Liabilities", "Total Current Liabilities"],
        "cash": ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents", "Cash And Short Term Investments", "Cash"],
        "inventory": ["Inventory", "Inventories", "Net Tangible Assets"],
        "operating_cash_flow": ["Operating Cash Flow", "Cash Flow From Operating Activities", "Net Cash Provided By Operating Activities"],
        "capex": ["Capital Expenditure", "Capital Expenditures", "Net PPE Purchase And Sale", "Purchase Of Property Plant And Equipment"],
        "free_cash_flow": ["Free Cash Flow"],
        "long_term_debt": ["Long Term Debt", "Long Term Debt Total", "LongTermDebt", "Total Non Current Liabilities Net Minority Interest"]
    }

    @classmethod
    def get_financial_value(cls, statement_dict: dict, standard_key: str, date_str: str) -> float:
        """
        Extracts a financial value using key mappings for a specific date string.
        """
        possible_keys = cls.KEY_MAPPINGS.get(standard_key, [])
        for pk in possible_keys:
            if pk in statement_dict:
                val = statement_dict[pk].get(date_str)
                if val is not None and not pd.isna(val):
                    return float(val)
        
        # Special case: compute free cash flow if missing but OCF and CapEx are available
        if standard_key == "free_cash_flow":
            ocf = cls.get_financial_value(statement_dict, "operating_cash_flow", date_str)
            capex = cls.get_financial_value(statement_dict, "capex", date_str)
            if ocf is not None:
                # CapEx is usually negative in cash flow statements, but sometimes positive in yfinance
                # If negative, we add it. If positive, we subtract it. Let's force negative capex subtraction.
                capex_val = abs(capex) if capex is not None else 0
                return ocf - capex_val
                
        # Special case: gross profit = revenue - cost of revenue
        if standard_key == "gross_profit":
            rev = cls.get_financial_value(statement_dict, "revenue", date_str)
            if rev is not None:
                # Try to find cost of revenue
                cogs = None
                for pk in ["Cost Of Revenue", "Cost of Revenue"]:
                    if pk in statement_dict:
                        cogs_val = statement_dict[pk].get(date_str)
                        if cogs_val is not None and not pd.isna(cogs_val):
                            cogs = float(cogs_val)
                            break
                if cogs is not None:
                    return rev - abs(cogs)
        
        return 0.0

    @classmethod
    def standardize_financials(cls, financials: dict) -> pd.DataFrame:
        """
        Converts raw yfinance statement dicts into a standardized DataFrame indexed by Date.
        """
        income = financials.get("income", {})
        balance = financials.get("balance", {})
        cashflow = financials.get("cashflow", {})
        
        # Convert all statements from {date: {field: value}} to {field: {date: value}}
        combined_stmt = {}
        all_dates = set()
        for stmt in [income, balance, cashflow]:
            for date_str, fields in stmt.items():
                all_dates.add(date_str)
                for field_name, val in fields.items():
                    if field_name not in combined_stmt:
                        combined_stmt[field_name] = {}
                    combined_stmt[field_name][date_str] = val
                
        sorted_dates = sorted(list(all_dates))
        
        records = []
        for date_str in sorted_dates:
                    
            row = {"Date": date_str}
            for std_key in cls.KEY_MAPPINGS.keys():
                row[std_key] = cls.get_financial_value(combined_stmt, std_key, date_str)
            
            # Additional derived fields
            # ROE = Net Income / Equity
            net_inc = row["net_income"]
            eq = row["equity"]
            row["roe"] = (net_inc / eq) if eq and eq != 0 else 0.0
            
            # Current Ratio = Current Assets / Current Liabilities
            ca = row["current_assets"]
            cl = row["current_liabilities"]
            row["current_ratio"] = (ca / cl) if cl and cl != 0 else 0.0
            
            # Debt to Equity = Liabilities / Equity
            liab = row["liabilities"]
            row["debt_to_equity"] = (liab / eq) if eq and eq != 0 else 0.0
            
            records.append(row)
            
        df = pd.DataFrame(records)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date").reset_index(drop=True)
        return df

    @classmethod
    def process(cls, raw_data: dict) -> dict:
        """
        Cleans prices, standardizes financials, and merges them into a aligned daily DataFrame.
        """
        # Convert prices to DataFrame
        df_price = pd.DataFrame(raw_data["price"])
        df_price["Date"] = pd.to_datetime(df_price["Date"])
        df_price = df_price.sort_values("Date").reset_index(drop=True)
        
        # Convert revenue to DataFrame
        df_rev = pd.DataFrame(raw_data["revenue"])
        df_rev["Date"] = pd.to_datetime(df_rev["Date"])
        df_rev = df_rev.sort_values("Date").reset_index(drop=True)
        
        # Standardize financials
        df_fin = cls.standardize_financials(raw_data["financials"])
        
        # Merge financials with price (Time alignment via forward fill)
        # We perform an outer merge on Date, then forward-fill the financial metrics, and filter to price dates
        df_merged = pd.merge(df_price, df_fin, on="Date", how="outer", suffixes=("", "_fin"))
        df_merged = df_merged.sort_values("Date").reset_index(drop=True)
        
        # Forward fill fundamental metrics
        fundamental_cols = [col for col in df_fin.columns if col != "Date"]
        df_merged[fundamental_cols] = df_merged[fundamental_cols].ffill()
        df_merged[fundamental_cols] = df_merged[fundamental_cols].fillna(0.0) # Fill initial values before first statement
        
        # Keep only the rows where price data actually exists
        df_aligned = df_merged[df_merged["Close"].notna()].copy()
        
        # Convert date column back to string for clean serialization
        df_aligned["Date"] = df_aligned["Date"].dt.strftime("%Y-%m-%d")
        df_rev["Date"] = df_rev["Date"].dt.strftime("%Y-%m-%d")
        
        # Extract metadata
        info = raw_data["financials"]["info"]
        
        return {
            "ticker": raw_data["ticker"],
            "info": info,
            "daily_data": df_aligned.to_dict(orient="records"),
            "monthly_revenue": df_rev.to_dict(orient="records"),
            "quarterly_financials": df_fin.assign(Date=df_fin["Date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records"),
            "source": raw_data["source"],
            "timestamp": raw_data["timestamp"]
        }
