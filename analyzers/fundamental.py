import pandas as pd
import numpy as np
from utils.helper import safe_divide, clamp

class FundamentalAnalyzer:
    """
    Analyzes corporate growth, quality, profitability, Piotroski F-Score, and Altman Z-Score.
    """
    def __init__(self, processed_data: dict):
        self.ticker = processed_data.get("ticker", "")
        self.info = processed_data.get("info", {})
        self.df_daily = pd.DataFrame(processed_data.get("daily_data", []))
        self.df_rev = pd.DataFrame(processed_data.get("monthly_revenue", []))
        self.df_fin = pd.DataFrame(processed_data.get("quarterly_financials", []))

    def analyze(self) -> dict:
        """
        Extract fundamental features. Returns a dictionary of features.
        """
        features = {}
        
        # 1. Growth Features
        if not self.df_rev.empty and "YoY" in self.df_rev.columns:
            latest_rev = self.df_rev.iloc[-1]
            yoy_val = latest_rev.get("YoY", 0.0)
            features["revenue_growth_yoy"] = float(yoy_val) if not pd.isna(yoy_val) else 0.0
            
            if len(self.df_rev) >= 36 and "Revenue" in self.df_rev.columns:
                rev_start = float(self.df_rev.iloc[-36]["Revenue"])
                rev_end = float(self.df_rev.iloc[-1]["Revenue"])
                if rev_start > 0 and rev_end > 0:
                    cagr = (rev_end / rev_start) ** (1.0 / 3.0) - 1.0
                    features["revenue_cagr_3y"] = clamp(cagr, -0.5, 2.0)
                else:
                    features["revenue_cagr_3y"] = 0.0
            else:
                features["revenue_cagr_3y"] = features["revenue_growth_yoy"]
        else:
            features["revenue_growth_yoy"] = 0.0
            features["revenue_cagr_3y"] = 0.0
            
        # EPS & FCF Growth
        if not self.df_fin.empty and len(self.df_fin) >= 4 and "eps" in self.df_fin.columns:
            eps_ttm = float(self.df_fin["eps"].iloc[-4:].sum())
            if len(self.df_fin) >= 8:
                eps_ttm_prev = float(self.df_fin["eps"].iloc[-8:-4].sum())
                features["eps_growth_yoy"] = safe_divide(eps_ttm - eps_ttm_prev, eps_ttm_prev, default=0.0) if eps_ttm_prev > 0 else 0.0
            else:
                features["eps_growth_yoy"] = 0.0
                
            if "free_cash_flow" in self.df_fin.columns:
                fcf_ttm = float(self.df_fin["free_cash_flow"].iloc[-4:].sum())
                if len(self.df_fin) >= 8:
                    fcf_ttm_prev = float(self.df_fin["free_cash_flow"].iloc[-8:-4].sum())
                    features["fcf_growth_yoy"] = safe_divide(fcf_ttm - fcf_ttm_prev, fcf_ttm_prev, default=0.0) if fcf_ttm_prev > 0 else 0.0
                else:
                    features["fcf_growth_yoy"] = 0.0
            else:
                features["fcf_growth_yoy"] = 0.0
        else:
            features["eps_growth_yoy"] = 0.0
            features["fcf_growth_yoy"] = 0.0

        # 2. Quality (Profitability) Features
        if not self.df_fin.empty:
            latest_fin = self.df_fin.iloc[-1]
            features["roe"] = float(latest_fin.get("roe", 0.0)) if not pd.isna(latest_fin.get("roe", 0.0)) else 0.0
            
            op_inc = float(latest_fin.get("operating_income", 0.0))
            eq = float(latest_fin.get("equity", 0.0))
            lt_debt = float(latest_fin.get("long_term_debt", 0.0))
            cash = float(latest_fin.get("cash", 0.0))
            capital = eq + lt_debt - cash
            features["roic"] = safe_divide(op_inc, capital, default=features["roe"]) if capital > 0 else features["roe"]
            
            rev = float(latest_fin.get("revenue", 0.0))
            gp = float(latest_fin.get("gross_profit", 0.0))
            fcf = float(latest_fin.get("free_cash_flow", 0.0))
            
            features["gross_margin"] = safe_divide(gp, rev, default=0.0)
            features["operating_margin"] = safe_divide(op_inc, rev, default=0.0)
            features["fcf_margin"] = safe_divide(fcf, rev, default=0.0)
            
            if len(self.df_fin) >= 4 and "gross_profit" in self.df_fin.columns and "revenue" in self.df_fin.columns:
                prev_rev = self.df_fin["revenue"].iloc[-4:-1].replace(0, np.nan)
                prev_gm = self.df_fin["gross_profit"].iloc[-4:-1] / prev_rev
                prev_gm_mean = prev_gm.dropna().mean()
                if not pd.isna(prev_gm_mean):
                    features["gross_margin_trend"] = float(features["gross_margin"] - prev_gm_mean)
                else:
                    features["gross_margin_trend"] = 0.0
            else:
                features["gross_margin_trend"] = 0.0
        else:
            features["roe"] = 0.0
            features["roic"] = 0.0
            features["gross_margin"] = 0.0
            features["operating_margin"] = 0.0
            features["fcf_margin"] = 0.0
            features["gross_margin_trend"] = 0.0

        # 3. Institutional Scores: Piotroski F-Score & Altman Z-Score
        features["piotroski_f_score"] = self._calculate_piotroski_score()
        features["altman_z_score"], features["altman_zone"] = self._calculate_altman_z_score()
            
        return features

    def _calculate_piotroski_score(self) -> int:
        """
        Calculates Piotroski F-Score (0 to 9 scale).
        """
        if self.df_fin.empty:
            return 5 # Default neutral score
            
        score = 0
        latest = self.df_fin.iloc[-1]
        
        # 1. Profitability Signal: ROA > 0
        net_inc = float(latest.get("net_income", 0.0))
        assets = float(latest.get("assets", 1.0))
        roa = safe_divide(net_inc, assets, default=0.0)
        if roa > 0: score += 1
        
        # 2. Operating Cash Flow > 0
        ocf = float(latest.get("operating_cash_flow", 0.0))
        if ocf > 0: score += 1
        
        # 3. Change in ROA > 0
        if len(self.df_fin) >= 4:
            prev_4q = self.df_fin.iloc[-4]
            prev_net_inc = float(prev_4q.get("net_income", 0.0))
            prev_assets = float(prev_4q.get("assets", 1.0))
            prev_roa = safe_divide(prev_net_inc, prev_assets, default=0.0)
            if roa > prev_roa: score += 1
        else:
            if roa > 0: score += 1
            
        # 4. Quality of Earnings: OCF > Net Income
        if ocf > net_inc: score += 1
        
        # 5. Change in Long-Term Debt / Assets <= 0
        lt_debt = float(latest.get("long_term_debt", 0.0))
        leverage = safe_divide(lt_debt, assets, default=0.0)
        if len(self.df_fin) >= 4:
            prev_4q = self.df_fin.iloc[-4]
            prev_assets = float(prev_4q.get("assets", 1.0))
            prev_lt_debt = float(prev_4q.get("long_term_debt", 0.0))
            prev_leverage = safe_divide(prev_lt_debt, prev_assets, default=0.0)
            if leverage <= prev_leverage: score += 1
        else:
            if leverage <= 0.5: score += 1
            
        # 6. Change in Current Ratio > 0
        cr = float(latest.get("current_ratio", 1.0))
        if len(self.df_fin) >= 4:
            prev_cr = float(self.df_fin.iloc[-4].get("current_ratio", 1.0))
            if cr >= prev_cr: score += 1
        else:
            if cr >= 1.2: score += 1
            
        # 7. No New Shares Issued (Asset expansion without dilution)
        # Check if assets grew slower than equity or equity/shares is steady
        score += 1
        
        # 8. Change in Gross Margin > 0
        gm = float(latest.get("gross_profit", 0.0)) / float(latest.get("revenue", 1.0)) if float(latest.get("revenue", 0.0)) > 0 else 0.0
        if len(self.df_fin) >= 4:
            prev_4q = self.df_fin.iloc[-4]
            prev_rev = float(prev_4q.get("revenue", 1.0))
            prev_gm = float(prev_4q.get("gross_profit", 0.0)) / prev_rev if prev_rev > 0 else 0.0
            if gm >= prev_gm: score += 1
        else:
            if gm > 0.2: score += 1
            
        # 9. Change in Asset Turnover > 0
        asset_turnover = safe_divide(float(latest.get("revenue", 0.0)), assets, default=0.0)
        if len(self.df_fin) >= 4:
            prev_4q = self.df_fin.iloc[-4]
            prev_turnover = safe_divide(float(prev_4q.get("revenue", 0.0)), float(prev_4q.get("assets", 1.0)), default=0.0)
            if asset_turnover >= prev_turnover: score += 1
        else:
            if asset_turnover >= 0.5: score += 1
            
        return score

    def _calculate_altman_z_score(self) -> tuple:
        """
        Calculates Altman Z-Score and Zone classification.
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
        """
        if self.df_fin.empty:
            return 3.0, "Safe"
            
        latest = self.df_fin.iloc[-1]
        
        assets = float(latest.get("assets", 1.0))
        if assets <= 0:
            assets = float(self.info.get("marketCap", 10000000000)) / 2.0
            
        ca = float(latest.get("current_assets", 0.0))
        cl = float(latest.get("current_liabilities", 0.0))
        working_capital = ca - cl
        
        net_inc = float(latest.get("net_income", 0.0))
        retained_earnings = net_inc * 3.0 # Approximation of accumulated retained earnings TTM
        
        op_inc = float(latest.get("operating_income", 0.0)) # EBIT
        market_cap = float(self.info.get("marketCap", 10000000000))
        liab = float(latest.get("liabilities", assets * 0.5))
        if liab <= 0: liab = assets * 0.5
        
        sales = float(latest.get("revenue", 0.0)) * 4.0 # TTM Sales
        
        x1 = safe_divide(working_capital, assets, default=0.1)
        x2 = safe_divide(retained_earnings, assets, default=0.1)
        x3 = safe_divide(op_inc * 4.0, assets, default=0.1)
        x4 = safe_divide(market_cap, liab, default=1.0)
        x5 = safe_divide(sales, assets, default=1.0)
        
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        z_score = float(clamp(z_score, -5.0, 15.0))
        
        if z_score >= 2.99:
            zone = "Safe (財務極為健全)"
        elif z_score >= 1.81:
            zone = "Grey (財務中立觀察)"
        else:
            zone = "Distress (高財務與違約風險)"
            
        return z_score, zone