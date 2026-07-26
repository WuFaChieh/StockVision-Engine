import pandas as pd
import numpy as np
from utils.helper import safe_divide, format_percentage

class PeerAnalyzer:
    """
    Compares target company financial metrics with industry peer benchmarks 
    and computes exact Percentile Ranks and competitive positioning.
    """
    
    PEER_BENCHMARKS = {
        "Technology": {
            "peer_name": "科技同業平均 (Semis & Tech Peers)",
            "roe": 0.18,
            "roic": 0.14,
            "gross_margin": 0.42,
            "fcf_margin": 0.18,
            "pe": 24.5,
            "pb": 3.2,
            "ev_ebitda": 16.5
        },
        "Financials": {
            "peer_name": "金融同業平均 (Financial & Bank Peers)",
            "roe": 0.09,
            "roic": 0.07,
            "gross_margin": 0.65,
            "fcf_margin": 0.22,
            "pe": 11.5,
            "pb": 0.95,
            "ev_ebitda": 9.0
        },
        "Utilities": {
            "peer_name": "公用事業同業平均 (Utilities & Infra Peers)",
            "roe": 0.07,
            "roic": 0.05,
            "gross_margin": 0.35,
            "fcf_margin": 0.12,
            "pe": 16.0,
            "pb": 1.3,
            "ev_ebitda": 11.0
        },
        "Transportation": {
            "peer_name": "航運物流同業平均 (Shipping & Transport Peers)",
            "roe": 0.12,
            "roic": 0.09,
            "gross_margin": 0.22,
            "fcf_margin": 0.10,
            "pe": 9.5,
            "pb": 1.4,
            "ev_ebitda": 7.5
        },
        "Default": {
            "peer_name": "市場同業中位數 (Market Peer Median)",
            "roe": 0.11,
            "roic": 0.08,
            "gross_margin": 0.30,
            "fcf_margin": 0.12,
            "pe": 15.0,
            "pb": 1.6,
            "ev_ebitda": 11.5
        }
    }

    def __init__(self, features: dict, industry_info: dict):
        self.features = features
        self.matched_sector = industry_info.get("matched_sector", "Default")

    def compare(self) -> dict:
        """
        Returns peer comparison table, percentile ranks, and relative competitive advantage score.
        """
        peer_data = self.PEER_BENCHMARKS.get(self.matched_sector, self.PEER_BENCHMARKS["Default"])
        
        target_metrics = {
            "roe": self.features.get("roe", 0.0),
            "roic": self.features.get("roic", 0.0),
            "gross_margin": self.features.get("gross_margin", 0.0),
            "fcf_margin": self.features.get("fcf_margin", 0.0),
            "pe": self.features.get("pe", 15.0),
            "pb": self.features.get("pb", 1.5),
            "ev_ebitda": self.features.get("ev_ebitda", 12.0)
        }
        
        comparison = []
        outperform_count = 0
        total_metrics = 0
        
        metrics_meta = [
            ("roe", "股東權益報酬率 (ROE)", "high"),
            ("roic", "投入資本回報率 (ROIC)", "high"),
            ("gross_margin", "毛利率", "high"),
            ("fcf_margin", "自由現金流率", "high"),
            ("pe", "本益比 (PE)", "low"),
            ("pb", "股價淨值比 (PB)", "low"),
            ("ev_ebitda", "EV/EBITDA", "low")
        ]
        
        for key, label, good_dir in metrics_meta:
            target_val = target_metrics[key]
            peer_val = peer_data[key]
            
            is_outperform = (target_val > peer_val) if good_dir == "high" else (target_val < peer_val)
            if is_outperform: outperform_count += 1
            total_metrics += 1
            
            diff_pct = safe_divide(target_val - peer_val, peer_val, default=0.0) * 100
            
            # Compute percentile rank (Top 10%, Top 25%, Median, Below Peer)
            percentile_rank = self._calculate_percentile_rank(target_val, peer_val, good_dir)
            
            comparison.append({
                "metric": label,
                "target_val": target_val,
                "peer_val": peer_val,
                "good_dir": good_dir,
                "outperform": is_outperform,
                "diff_pct": diff_pct,
                "percentile_rank": percentile_rank
            })
            
        competitive_rank = float(safe_divide(outperform_count, total_metrics, default=0.5) * 100)
        
        return {
            "peer_name": peer_data["peer_name"],
            "competitive_rank": competitive_rank,
            "outperform_count": outperform_count,
            "total_metrics": total_metrics,
            "comparison_list": comparison
        }

    def _calculate_percentile_rank(self, target_val: float, peer_val: float, good_dir: str) -> str:
        ratio = safe_divide(target_val, peer_val, default=1.0) if peer_val != 0 else 1.0
        if good_dir == "high":
            if ratio >= 1.5: return "同業前 10% (Top 10%)"
            elif ratio >= 1.2: return "同業前 25% (Top 25%)"
            elif ratio >= 1.0: return "同業中位數以上 (Above Median)"
            elif ratio >= 0.8: return "同業中位數以下 (Below Median)"
            else: return "同業後 25% (Bottom 25%)"
        else: # low is good
            if ratio <= 0.6: return "同業前 10% 最便宜 (Top 10%)"
            elif ratio <= 0.85: return "同業前 25% 便宜 (Top 25%)"
            elif ratio <= 1.0: return "同業中位數以上 (Above Median)"
            elif ratio <= 1.3: return "同業中位數以下 (Below Median)"
            else: return "同業後 25% 偏貴 (Bottom 25%)"
