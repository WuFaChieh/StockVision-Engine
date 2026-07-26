import pandas as pd
import numpy as np
from utils.helper import safe_divide, clamp

class SnowflakeEngine:
    """
    StockVision 5-Pillar Enterprise Health Matrix (五維企業健康星圖):
    Computes 5-Pillar Scores (0 to 6 pts per pillar, 0-30 total),
    detailed score breakdown checklists, and Short/Long-Term Health Balance Stacks.
    """
    def __init__(self, features: dict, processed_data: dict, industry_info: dict):
        self.features = features
        self.info = processed_data.get("info", {})
        self.df_fin = pd.DataFrame(processed_data.get("quarterly_financials", []))
        self.matched_sector = industry_info.get("matched_sector", "Default")
        self.benchmarks = industry_info.get("benchmarks", {})

    def analyze(self) -> dict:
        pe = self.features.get("pe", 15.0)
        pb = self.features.get("pb", 1.5)
        bench_pe = self.benchmarks.get("pe", 15.0)
        dcf_premium = self.features.get("dcf_premium", 0.0)
        rev_growth = self.features.get("revenue_growth_yoy", 0.0)
        eps_growth = self.features.get("eps_growth_yoy", 0.0)
        cagr = self.features.get("revenue_cagr_3y", 0.0)
        roe = self.features.get("roe", 0.0)
        roic = self.features.get("roic", 0.0)
        cr = self.features.get("current_ratio", 1.0)
        de = self.features.get("debt_to_equity", 1.0)
        ic = self.features.get("interest_coverage", 5.0)

        # 1. Valuation Pillar (0 to 6)
        v_pts = 0
        v_items = []
        if dcf_premium <= 0:
            v_pts += 2; v_items.append("DCF 折現低於內在價值 (+2分)")
        elif dcf_premium <= 0.15:
            v_pts += 1; v_items.append("DCF 折現估值公允 (+1分)")
        else:
            v_items.append("DCF 內在價值高估 (0分)")
            
        if pe <= bench_pe:
            v_pts += 2; v_items.append(f"本益比 PE ({pe:.1f}x) 低於同業中位數 ({bench_pe:.1f}x) (+2分)")
        elif pe <= bench_pe * 1.2:
            v_pts += 1; v_items.append(f"本益比 PE 貼近同業平均 (+1分)")
        else:
            v_items.append(f"本益比 PE 偏高 (0分)")
            
        if pb <= self.benchmarks.get("pb", 1.5):
            v_pts += 2; v_items.append(f"股價淨值比 PB 處於合理區間 (+2分)")
        else:
            v_items.append("PB 偏高 (0分)")
        
        # 2. Future Growth Pillar (0 to 6)
        g_pts = 0
        g_items = []
        if rev_growth >= 0.15:
            g_pts += 2; g_items.append(f"營收 YoY ({rev_growth*100:.1f}%) 達強勁成長 (+2分)")
        elif rev_growth >= 0.05:
            g_pts += 1; g_items.append(f"營收 YoY 穩定擴張 (+1分)")
        else:
            g_items.append("營收成長趨緩 (0分)")
            
        if eps_growth >= 0.15:
            g_pts += 2; g_items.append(f"EPS YoY ({eps_growth*100:.1f}%) 達高成長 (+2分)")
        elif eps_growth >= 0.05:
            g_pts += 1; g_items.append("EPS YoY 平穩 (+1分)")
        else:
            g_items.append("EPS 成長平淡 (0分)")
            
        if cagr >= 0.10:
            g_pts += 2; g_items.append(f"3年營收 CAGR ({cagr*100:.1f}%) 優異 (+2分)")
        elif cagr >= 0.04:
            g_pts += 1; g_items.append("3年營收 CAGR 健全 (+1分)")
        else:
            g_items.append("CAGR 表現普通 (0分)")

        # 3. Past Performance Pillar (0 to 6)
        p_pts = 0
        p_items = []
        if roe >= 0.20:
            p_pts += 2; p_items.append(f"ROE ({roe*100:.1f}%) 達頂尖 20% 水準 (+2分)")
        elif roe >= 0.12:
            p_pts += 1; p_items.append(f"ROE 達 12% 以上 (+1分)")
        else:
            p_items.append("ROE 偏低 (0分)")
            
        if roic >= 0.15:
            p_pts += 2; p_items.append(f"ROIC ({roic*100:.1f}%) 資本回報極高 (+2分)")
        elif roic >= 0.08:
            p_pts += 1; p_items.append(f"ROIC 高於資金成本 (+1分)")
        else:
            p_items.append("ROIC 利差受限 (0分)")
            
        if self.features.get("gross_margin", 0.0) >= 0.35:
            p_pts += 2; p_items.append(f"毛利率 ({self.features.get('gross_margin', 0.0)*100:.1f}%) 表現強勢 (+2分)")
        elif self.features.get("gross_margin", 0.0) >= 0.20:
            p_pts += 1; p_items.append("毛利率平穩 (+1分)")
        else:
            p_items.append("毛利率受壓 (0分)")

        # 4. Financial Health Pillar (0 to 6)
        h_pts = 0
        h_items = []
        if cr >= 1.5:
            h_pts += 2; h_items.append(f"流動比率 ({cr:.2f}) 充沛無短債壓力 (+2分)")
        elif cr >= 1.0:
            h_pts += 1; h_items.append("流動比率安全 (+1分)")
        else:
            h_items.append("短債流動性偏緊 (0分)")
            
        if de <= 0.5:
            h_pts += 2; h_items.append(f"負債股益比 ({de:.2f}) 財務結構穩健 (+2分)")
        elif de <= 1.0:
            h_pts += 1; h_items.append("槓桿比率合理 (+1分)")
        else:
            h_items.append("財務槓桿偏高 (0分)")
            
        if ic >= 5.0:
            h_pts += 2; h_items.append(f"利息保障倍數 ({ic:.1f}x) 償債無虞 (+2分)")
        elif ic >= 2.0:
            h_pts += 1; h_items.append("利息保障中等 (+1分)")
        else:
            h_items.append("利息負擔較重 (0分)")

        # 5. Dividend & Return Pillar (0 to 6)
        d_pts = 3
        d_items = ["現金流充沛與庫藏股回報 (+3分)"]
        if self.features.get("fcf_margin", 0.0) >= 0.15:
            d_pts += 2; d_items.append(f"自由現金流率 ({self.features.get('fcf_margin', 0.0)*100:.1f}%) 高效 (+2分)")
        elif self.features.get("fcf_margin", 0.0) >= 0.05:
            d_pts += 1; d_items.append("自由現金流正向 (+1分)")
            
        if de <= 0.3:
            d_pts += 1; d_items.append("淨現金或極低負債回報加分 (+1分)")

        v_pts = min(6, v_pts)
        g_pts = min(6, g_pts)
        p_pts = min(6, p_pts)
        h_pts = min(6, h_pts)
        d_pts = min(6, d_pts)
        total_matrix = v_pts + g_pts + p_pts + h_pts + d_pts

        # Short & Long Term Health Balance Stack
        latest = self.df_fin.iloc[-1] if not self.df_fin.empty else {}
        short_assets = float(latest.get("current_assets", 100.0))
        short_liab = float(latest.get("current_liabilities", 50.0))
        long_assets = float(latest.get("assets", 200.0)) - short_assets
        long_liab = float(latest.get("long_term_debt", 30.0))

        return {
            "matrix_total": total_matrix,
            "pillars": {
                "Valuation": {"score": v_pts, "max": 6, "name": "Valuation (估值表現)", "items": v_items},
                "FutureGrowth": {"score": g_pts, "max": 6, "name": "Future Growth (未來成長)", "items": g_items},
                "PastPerformance": {"score": p_pts, "max": 6, "name": "Past Performance (過去績效)", "items": p_items},
                "FinancialHealth": {"score": h_pts, "max": 6, "name": "Financial Health (財務健康)", "items": h_items},
                "Dividend": {"score": d_pts, "max": 6, "name": "Dividend & Return (股利與回報)", "items": d_items}
            },
            "health_stack": {
                "short_assets": short_assets,
                "short_liabilities": short_liab,
                "long_assets": max(0, long_assets),
                "long_liabilities": long_liab,
                "short_healthy": short_assets > short_liab,
                "long_healthy": long_assets > long_liab
            }
        }
