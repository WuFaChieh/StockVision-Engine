import pandas as pd
import numpy as np
from utils.helper import safe_divide, clamp

class RiskAnalyzer:
    """
    Analyzes corporate financial risk, solvency, operational efficiency, 
    and categorized multi-dimensional Risk Radar (Geopolitical, FX, Concentration, Tech/Reg, Cyclical, Liquidity).
    """
    def __init__(self, processed_data: dict):
        self.ticker = processed_data.get("ticker", "")
        self.info = processed_data.get("info", {})
        self.df_fin = pd.DataFrame(processed_data.get("quarterly_financials", []))
        self.df_daily = pd.DataFrame(processed_data.get("daily_data", []))

    def analyze(self) -> dict:
        """
        Extract risk and safety features. Returns a dictionary of features.
        """
        features = {}
        
        # Systematic risk (Beta)
        features["beta"] = float(self.info.get("beta", 1.0))
        
        if not self.df_fin.empty:
            latest_fin = self.df_fin.iloc[-1]
            
            features["debt_to_equity"] = float(latest_fin.get("debt_to_equity", 1.0))
            features["current_ratio"] = float(latest_fin.get("current_ratio", 1.0))
            
            op_inc = float(latest_fin.get("operating_income", 0.0))
            lt_debt = float(latest_fin.get("long_term_debt", 0.0))
            interest_expense = lt_debt * 0.04
            
            if interest_expense > 0:
                features["interest_coverage"] = safe_divide(op_inc, interest_expense, default=1.0)
            else:
                features["interest_coverage"] = 999.0 if op_inc > 0 else -1.0
                
            rev = float(latest_fin.get("revenue", 0.0))
            gp = float(latest_fin.get("gross_profit", 0.0))
            cogs = rev - gp
            inv = float(latest_fin.get("inventory", 0.0))
            if inv > 0:
                features["inventory_turnover"] = safe_divide(cogs, inv, default=10.0)
            else:
                features["inventory_turnover"] = 10.0
        else:
            features["debt_to_equity"] = 1.0
            features["current_ratio"] = 1.0
            features["interest_coverage"] = 1.0
            features["inventory_turnover"] = 5.0
            
        # Categorized Risk Radar (0-100 scale, higher = higher risk)
        features["risk_radar"] = self._calculate_risk_radar(features)
        features["categorized_risks"] = self._calculate_categorized_risks(features)
        
        return features

    def _calculate_risk_radar(self, base_features: dict) -> dict:
        ic = base_features.get("interest_coverage", 5.0)
        cr = base_features.get("current_ratio", 1.0)
        beta = base_features.get("beta", 1.0)
        inv_turnover = base_features.get("inventory_turnover", 5.0)
        de = base_features.get("debt_to_equity", 1.0)
        
        solvency = clamp(40.0 - ic * 3.0 + (2.0 - cr) * 20.0, 10.0, 95.0)
        operational = clamp(50.0 - inv_turnover * 4.0, 10.0, 90.0)
        volatility = clamp(beta * 40.0 + 10.0, 10.0, 95.0)
        leverage = clamp(de * 35.0, 10.0, 95.0)
        asset_quality = 25.0
        
        return {
            "Solvency": float(solvency),
            "Operational": float(operational),
            "Volatility": float(volatility),
            "Leverage": float(leverage),
            "AssetQuality": float(asset_quality)
        }

    def _calculate_categorized_risks(self, base_features: dict) -> dict:
        """
        Calculates detailed, specific risk scores and descriptions:
        - Geopolitical Risk
        - FX & Macro Risk
        - Client Concentration Risk
        - Tech & Regulatory Risk
        - Cyclical Risk
        - Liquidity Risk
        """
        sector = self.info.get("sector", "")
        beta = base_features.get("beta", 1.0)
        cr = base_features.get("current_ratio", 1.0)
        ic = base_features.get("interest_coverage", 5.0)
        
        # 1. Geopolitical Risk
        geo_score = 45.0
        geo_desc = "半導體與高科技產業跨國供應鏈地緣政治敏感度較高。" if sector in ["Technology", "Semiconductors"] else "地緣政治直接影響溫和，主要為大宗商品價格波動。"
        if sector in ["Technology", "Electronic Technology"]: geo_score = 65.0
        
        # 2. FX & Macro Risk
        fx_score = 55.0
        fx_desc = "外銷出口佔比高，營收受美元及區域匯率波動影響顯著。"
        
        # 3. Client Concentration Risk
        conc_score = 40.0
        conc_desc = "前五大客戶貢獻度中等，客戶過度集中風險可控。"
        if sector in ["Technology"]: conc_score = 60.0; conc_desc = "主要營收來自全球幾家頂級科技巨頭，客戶集中度偏高。"
        
        # 4. Tech & Regulatory Risk
        tech_score = 50.0
        tech_desc = "技術演進快速，研發資本支出高，需持續保持技術領先。"
        
        # 5. Cyclical Risk
        cyc_score = float(clamp(beta * 45.0, 20.0, 90.0))
        cyc_desc = "受半導體與全球電子產品景氣循環週期調控因素影響。"
        
        # 6. Liquidity Risk
        liq_score = float(clamp(50.0 - cr * 20.0 + (5.0 - ic) * 5.0, 10.0, 90.0))
        liq_desc = "流動比率與利息保障倍數充沛，無短期償債壓力。" if liq_score < 40 else "短期流動資產偏緊，需密切留意速動比率。"

        return {
            "geopolitical": {"score": geo_score, "name": "地緣政治風險", "desc": geo_desc},
            "fx_macro": {"score": fx_score, "name": "匯率與總體風險", "desc": fx_desc},
            "concentration": {"score": conc_score, "name": "客戶集中度風險", "desc": conc_desc},
            "tech_reg": {"score": tech_score, "name": "技術替代與法規風險", "desc": tech_desc},
            "cyclical": {"score": cyc_score, "name": "景氣循環波動風險", "desc": cyc_desc},
            "liquidity": {"score": liq_score, "name": "財務流動性風險", "desc": liq_desc}
        }
