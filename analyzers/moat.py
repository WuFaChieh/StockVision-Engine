import pandas as pd
import numpy as np
from utils.helper import safe_divide, clamp
from config import DEFAULT_RISK_FREE_RATE, DEFAULT_EQUITY_RISK_PREMIUM

class MoatAnalyzer:
    """
    StockVision Moat & Investment Checklist Engine:
    Evaluates 10-Item Comprehensive Investment Checklist and 4-Golden-Standard Economic Moat.
    Displays clear pass summary e.g. "8 / 10 項符合投資條件 (80% 通過率)".
    """
    def __init__(self, features: dict, processed_data: dict, industry_info: dict):
        self.features = features
        self.info = processed_data.get("info", {})
        self.df_fin = pd.DataFrame(processed_data.get("quarterly_financials", []))
        self.df_daily = pd.DataFrame(processed_data.get("daily_data", []))
        self.matched_sector = industry_info.get("matched_sector", "Default")

    def analyze(self) -> dict:
        roe = self.features.get("roe", 0.0)
        roic = self.features.get("roic", 0.0)
        gm = self.features.get("gross_margin", 0.0)
        fcf_margin = self.features.get("fcf_margin", 0.0)
        beta = self.features.get("beta", 1.0)
        market_cap = float(self.info.get("marketCap", 0))
        rev_growth = self.features.get("revenue_growth_yoy", 0.15)
        eps_growth = self.features.get("eps_growth_yoy", 0.15)
        debt_ratio = self.features.get("debt_to_equity", 0.35)
        pe = float(self.info.get("trailingPE", 20.0) or 20.0)
        dcf_premium = self.features.get("dcf_premium", 0.0)
        ma50 = self.features.get("ma50", 100.0)
        latest_close = self.df_daily["Close"].iloc[-1] if not self.df_daily.empty else 100.0
        
        # Estimate WACC
        wacc = clamp(DEFAULT_RISK_FREE_RATE + beta * DEFAULT_EQUITY_RISK_PREMIUM, 0.07, 0.12)
        roic_wacc_spread = roic - wacc
        
        # 1. 4 Golden Standards
        c1_pass = roic_wacc_spread >= 0.05
        c2_pass = gm >= 0.40
        c3_pass = fcf_margin >= 10.0 or fcf_margin >= 0.10
        c4_pass = market_cap >= 50000000000
        golden_passed_count = sum([c1_pass, c2_pass, c3_pass, c4_pass])
        
        # 2. Comprehensive 10-Item Investment Checklist
        c5_pass = rev_growth >= 0.10
        c6_pass = eps_growth >= 0.10
        c7_pass = roe >= 0.15
        c8_pass = debt_ratio <= 0.50
        c9_pass = pe <= 25.0 or dcf_premium <= 0.0
        c10_pass = latest_close >= ma50
        
        checklist_10_items = [
            {"item": "1. 超額利差 (ROIC - WACC >= 5%)", "passed": c1_pass, "actual": f"{roic_wacc_spread*100:.1f}%", "target": ">= 5.0%"},
            {"item": "2. 高定價權 (毛利率 Gross Margin >= 40%)", "passed": c2_pass, "actual": f"{gm*100:.1f}%", "target": ">= 40.0%"},
            {"item": "3. 自由現金流率 (FCF Margin >= 10%)", "passed": c3_pass, "actual": f"{fcf_margin if fcf_margin > 1.0 else fcf_margin*100:.1f}%", "target": ">= 10.0%"},
            {"item": "4. 產業龍頭規模 (市值 > $50B)", "passed": c4_pass, "actual": f"${market_cap/1e9:.1f}B", "target": "> $50.0B"},
            {"item": "5. 營收雙位數成長 (YoY >= 10%)", "passed": c5_pass, "actual": f"{rev_growth*100:.1f}%", "target": ">= 10.0%"},
            {"item": "6. 盈餘強勁成長 (EPS YoY >= 10%)", "passed": c6_pass, "actual": f"{eps_growth*100:.1f}%", "target": ">= 10.0%"},
            {"item": "7. 高股東權益報酬 (ROE >= 15%)", "passed": c7_pass, "actual": f"{roe*100:.1f}%", "target": ">= 15.0%"},
            {"item": "8. 穩健財務結構 (負債比率 < 50%)", "passed": c8_pass, "actual": f"{debt_ratio*100:.1f}%", "target": "< 50.0%"},
            {"item": "9. 估值安全邊際 (PE < 25x 或 DCF折價)", "passed": c9_pass, "actual": f"PE {pe:.1f}x", "target": "< 25.0x"},
            {"item": "10. 技術面強勢多頭 (股價 > 50日均線)", "passed": c10_pass, "actual": f"${latest_close:.1f}", "target": f">${ma50:.1f}"}
        ]
        
        passed_10_count = sum([item["passed"] for item in checklist_10_items])
        pass_rate_pct = (passed_10_count / 10.0) * 100.0

        # Golden Standards detail
        golden_standards_checklist = [
            {"standard": "超額利差 (ROIC - WACC >= 5%)", "target": ">= 5.0%", "actual": f"{roic_wacc_spread*100:.1f}%", "passed": c1_pass, "desc": f"實際 ROIC 利差達 +{roic_wacc_spread*100:.1f}%，反映高資本回報與再投資效益。"},
            {"standard": "高定價權 (毛利率 Gross Margin >= 40%)", "target": ">= 40.0%", "actual": f"{gm*100:.1f}%", "passed": c2_pass, "desc": f"實際毛利率為 {gm*100:.1f}%，顯示產品具備強大定價權與技術壁壘。"},
            {"standard": "自由現金流率 (FCF Margin >= 10%)", "target": ">= 10.0%", "actual": f"{fcf_margin if fcf_margin > 1.0 else fcf_margin*100:.1f}%", "passed": c3_pass, "desc": "提供強大資本支出與股息發放能力。"},
            {"standard": "產業龍頭規模 (市值 Market Cap > $50B)", "target": "> $50.0B", "actual": f"${market_cap/1e9:.1f}B", "passed": c4_pass, "desc": f"實際市值約 ${market_cap/1e9:.1f}B，在領域內具備顯著規模與門檻優勢。"}
        ]

        if golden_passed_count == 4:
            moat_rating = "Wide Moat (寬廣護城河)"
            moat_code = "Wide"
        elif golden_passed_count >= 2:
            moat_rating = "Narrow Moat (狹窄護城河)"
            moat_code = "Narrow"
        else:
            moat_rating = "No Moat (無顯著護城河)"
            moat_code = "None"

        present_sources = []
        if c1_pass and c2_pass:
            present_sources.append({"source": "Intangible Assets (無形資產/專利品牌)", "present": True, "desc": f"高達 {gm*100:.1f}% 毛利率與 ROIC 利差證實具備無形資產與專利定價溢價。"})
        if c3_pass and self.matched_sector in ["Technology", "Semiconductors", "Software"]:
            present_sources.append({"source": "Switching Costs (高客戶轉換成本)", "present": True, "desc": "客戶替換產品需面臨巨額重新認證與系統停機成本，黏著度極高。"})
        if c1_pass and c4_pass:
            present_sources.append({"source": "Cost Advantage (成本領先與規模效應)", "present": True, "desc": f"超額利差 +{roic_wacc_spread*100:.1f}% 與高市值展現規模經濟與良率領先優勢。"})
            
        if not present_sources:
            present_sources = [{"source": "Competitive Dynamics (自由競爭市場)", "present": False, "desc": "通過之黃金標準不足 2 項，產業門檻偏低，面對同業價格競爭壓力。"}]

        if roic_wacc_spread >= 0.06 and fcf_margin >= 0.10:
            cap_alloc = "Exemplary (極佳資本配置)"
        elif roic_wacc_spread >= 0.0 or fcf_margin >= 0.05:
            cap_alloc = "Standard (標準資本配置)"
        else:
            cap_alloc = "Poor (資本配置欠佳)"

        if dcf_premium <= -0.20:
            stars = 5
            star_desc = "5 星評等 (極度低估 5星首選)"
        elif dcf_premium <= -0.05:
            stars = 4
            star_desc = "4 星評等 (合理偏低估 4星特優)"
        elif dcf_premium <= 0.10:
            stars = 3
            star_desc = "3 星評等 (估值公允 3星觀望)"
        elif dcf_premium <= 0.25:
            stars = 2
            star_desc = "2 星評等 (估值偏高 2星減碼)"
        else:
            stars = 1
            star_desc = "1 星評等 (嚴重溢價 1星避開)"

        return {
            "moat_score": float(golden_passed_count * 25.0),
            "moat_rating": moat_rating,
            "moat_code": moat_code,
            "passed_golden_count": golden_passed_count,
            "golden_standards_checklist": golden_standards_checklist,
            "investment_checklist_10": {
                "passed_count": passed_10_count,
                "total_count": 10,
                "pass_rate_pct": pass_rate_pct,
                "summary_text": f"{passed_10_count} / 10 項符合投資條件 ({pass_rate_pct:.0f}% 通過率)",
                "items": checklist_10_items
            },
            "moat_sources": present_sources,
            "capital_allocation": cap_alloc,
            "star_rating": stars,
            "star_desc": star_desc,
            "roic_wacc_spread": roic_wacc_spread * 100.0,
            "wacc": wacc * 100.0
        }
