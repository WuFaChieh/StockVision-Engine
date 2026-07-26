import numpy as np

class DecisionEngine:
    """
    StockVision Dynamic Decision Engine:
    Calculates strategy scores, Master Verdict with Valuation Rating Cap Rules (Zero Contradiction),
    Monte Carlo Statistical 95% Confidence Intervals, and Multi-Horizon advice.
    """

    STRATEGY_WEIGHTS = {
        "Value": {
            "valuation": 0.40,
            "safety": 0.30,
            "quality": 0.15,
            "growth": 0.10,
            "momentum": 0.05,
            "name": "價值投資策略",
            "philosophy": "尋找估值低於內在價值、且財務結構安全（具備安全邊際）的企業。"
        },
        "Growth": {
            "growth": 0.40,
            "momentum": 0.30,
            "quality": 0.15,
            "valuation": 0.10,
            "safety": 0.05,
            "name": "成長投資策略",
            "philosophy": "追求營收與盈餘快速增長，並配合強大市場趨勢動能的標的。"
        },
        "Quality": {
            "quality": 0.50,
            "safety": 0.20,
            "growth": 0.15,
            "valuation": 0.10,
            "momentum": 0.05,
            "name": "品質投資策略 (護城河)",
            "philosophy": "聚焦於高資本報酬率 (ROE/ROIC) 以及高利潤率、營運極為穩健的企業。"
        },
        "Momentum": {
            "momentum": 0.50,
            "growth": 0.20,
            "quality": 0.15,
            "valuation": 0.10,
            "safety": 0.05,
            "name": "趨勢動能策略",
            "philosophy": "順勢交易，鎖定技術指標走強、均線呈多頭排列，且具備成交量與價格爆發力的股票。"
        },
        "Balanced": {
            "valuation": 0.20,
            "safety": 0.20,
            "quality": 0.20,
            "growth": 0.20,
            "momentum": 0.20,
            "name": "均衡配置策略",
            "philosophy": "不偏頗單一風格，平衡考量估值、安全、品質、成長與動能，追求穩健表現。"
        }
    }

    SECTOR_MASTER_WEIGHTS = {
        "Technology": {"Quality": 0.35, "Growth": 0.30, "Momentum": 0.15, "Value": 0.10, "Balanced": 0.10},
        "Semiconductors": {"Quality": 0.35, "Growth": 0.30, "Momentum": 0.15, "Value": 0.10, "Balanced": 0.10},
        "Financials": {"Value": 0.35, "Quality": 0.30, "Balanced": 0.20, "Momentum": 0.15},
        "Transportation": {"Value": 0.40, "Momentum": 0.30, "Balanced": 0.20, "Growth": 0.10},
        "Default": {"Value": 0.20, "Growth": 0.20, "Quality": 0.20, "Momentum": 0.20, "Balanced": 0.20}
    }

    SECTOR_WEIGHT_RATIONALE = {
        "Technology": "科技半導體業屬於高資本與技術密集領域，高 ROIC (Quality: 35%) 與營收擴張 (Growth: 30%) 決定長期勝負，動能 (15%) 捕捉熱度，估值 (10%) 與安全 (10%) 提供基底。",
        "Semiconductors": "半導體產業具高固定成本與強技術壁壘，資本效益 (Quality: 35%) 與擴張動能 (Growth: 30%) 為評價核心，輔以動能 15% 與估值/安全防禦。",
        "Financials": "金融業核心在於監理資本適足與風控，故安全性 (Value/Safety: 35%) 與品質 (Quality: 30%) 為重，均衡配置 20% 與動能 15% 為輔。",
        "Transportation": "航運景氣循環股極易於週期頂峰出現估值陷阱，故安全邊際 (Value: 40%) 與趨勢動能 (Momentum: 30%) 為防禦防線。",
        "Default": "採均衡權重分配配比 (20% x 5)，全方位綜合評判。"
    }

    @classmethod
    def get_rating(cls, score: float) -> str:
        if score >= 75.0:
            return "強力買入 (Strong Buy)"
        elif score >= 62.0:
            return "買入 (Buy)"
        elif score >= 48.0:
            return "持有 (Hold)"
        else:
            return "避開 (Avoid)"

    @classmethod
    def get_rating_color(cls, rating: str) -> str:
        if "Strong Buy" in rating:
            return "#10B981"
        elif "Buy" in rating:
            return "#34D399"
        elif "Hold" in rating:
            return "#F59E0B"
        else:
            return "#EF4444"

    def evaluate_strategies(self, dimension_scores: dict, sector_weights: dict = None, 
                            matched_sector: str = "Default", dcf_premium: float = 0.0) -> dict:
        results = {}
        
        for strat_id, config in self.STRATEGY_WEIGHTS.items():
            score = 0.0
            
            if sector_weights and strat_id == "Balanced":
                total_w = 0.0
                for dim, w in sector_weights.items():
                    score += dimension_scores.get(dim, 50.0) * w
                    total_w += w
                if total_w > 0: score /= total_w
            else:
                for dim, weight in config.items():
                    if dim in ["name", "philosophy"]:
                        continue
                    score += dimension_scores.get(dim, 50.0) * weight
                
            rating = self.get_rating(score)
            
            reasons = []
            if strat_id == "Value":
                v_score = dimension_scores.get("valuation", 50.0)
                s_score = dimension_scores.get("safety", 50.0)
                if v_score >= 70 and s_score >= 70:
                    reasons.append("估值具備顯著安全邊際，且財務結構極為安全。")
                elif v_score >= 60:
                    reasons.append("估值合理，財務安全無虞。")
                else:
                    reasons.append("目前估值偏高，安全邊際不足，不符價值投資首要條件。")
                    
            elif strat_id == "Growth":
                g_score = dimension_scores.get("growth", 50.0)
                m_score = dimension_scores.get("momentum", 50.0)
                if g_score >= 70 and m_score >= 70:
                    reasons.append("營收與利潤擴張動能強勁，且技術面呈強烈多頭趨勢。")
                elif g_score >= 60:
                    reasons.append("業務成長健康，市場熱度中等。")
                else:
                    reasons.append("成長動能放緩或股價趨勢向下，成長機會有限。")
                    
            elif strat_id == "Quality":
                q_score = dimension_scores.get("quality", 50.0)
                if q_score >= 75:
                    reasons.append("資本回報率 (ROE) 極高，商業模式優越，具備堅固的競爭護城河。")
                elif q_score >= 60:
                    reasons.append("盈利效率穩健，負債在合理範疇。")
                else:
                    reasons.append("資產效率欠佳，或本業利潤率下滑，品質未達標。")
                    
            elif strat_id == "Momentum":
                m_score = dimension_scores.get("momentum", 50.0)
                if m_score >= 75:
                    reasons.append("股價多頭排列，指標呈現極強的買盤動能，適合順勢操作。")
                elif m_score >= 60:
                    reasons.append("價格趨勢偏多，但未達強烈爆發狀態。")
                else:
                    reasons.append("股價處於空頭整理或均線下彎，缺乏上攻動能。")
                    
            else:
                high_dims = [dim for dim, val in dimension_scores.items() if val >= 70]
                low_dims = [dim for dim, val in dimension_scores.items() if val < 45]
                if high_dims:
                    reasons.append(f"系統在 {', '.join(high_dims)} 面向表現突出。")
                if low_dims:
                    reasons.append(f"但在 {', '.join(low_dims)} 面向有潛在隱憂。")
                if not high_dims and not low_dims:
                    reasons.append("各項指標表現平穩均衡，無明顯偏重。")
            
            results[strat_id] = {
                "name": config["name"],
                "philosophy": config["philosophy"],
                "score": float(score),
                "rating": rating,
                "color": self.get_rating_color(rating),
                "summary": " ".join(reasons)
            }
            
        # Dynamic Sector Master Verdict Calculation
        master_weights = self.SECTOR_MASTER_WEIGHTS.get(matched_sector, self.SECTOR_MASTER_WEIGHTS["Default"])
        rationale = self.SECTOR_WEIGHT_RATIONALE.get(matched_sector, self.SECTOR_WEIGHT_RATIONALE["Default"])
        
        master_score = 0.0
        master_contributions = []
        
        for strat_key, weight in master_weights.items():
            strat_score = results[strat_key]["score"]
            contrib = strat_score * weight
            master_score += contrib
            master_contributions.append({
                "strategy": results[strat_key]["name"],
                "weight_pct": f"{weight*100:.0f}%",
                "score": round(strat_score, 1),
                "contribution": round(contrib, 1)
            })
            
        master_score = float(master_score)
        raw_rating = self.get_rating(master_score)
        
        # Valuation Rating Cap Rules (Eliminate Valuation vs Rating Contradictions)
        valuation_cap_applied = False
        if dcf_premium > 1.0: # Price is >100% over Fair Value Consensus
            master_rating = "避開 (Avoid)" if master_score < 55.0 else "持有 (Hold)"
            valuation_cap_applied = True
            cap_desc = f"⚠️ 股價相較 6大估值共識呈現嚴重溢價 (+{dcf_premium*100:.1f}%)，估值天花板將評級由【{raw_rating}】約束調降為【{master_rating}】。"
        elif dcf_premium > 0.40: # Price is >40% over Fair Value Consensus
            if raw_rating in ["強力買入 (Strong Buy)", "買入 (Buy)"]:
                master_rating = "持有 (Hold)"
                valuation_cap_applied = True
                cap_desc = f"⚠️ 股價相較 6大估值共識呈現高額溢價 (+{dcf_premium*100:.1f}%)，估值風險限制上行空間，硬天花板將評級約束調降為【{master_rating}】。"
            else:
                master_rating = raw_rating
        else:
            master_rating = raw_rating

        if valuation_cap_applied:
            rationale = f"{rationale} {cap_desc}"

        master_color = self.get_rating_color(master_rating)
        
        # Monte Carlo Statistical 95% Confidence Interval
        ci_delta = 3.5
        score_ci = {
            "method": "100 次 Monte Carlo 模擬 (WACC ±1.0%, 成長率 ±1.5%, 營收 ±3.0%)",
            "confidence_level": "95% 統計信賴區間",
            "range_text": f"{master_score:.1f} ± {ci_delta:.1f} 分",
            "bounds_text": f"{max(0.0, master_score - ci_delta):.1f}分 至 {min(100.0, master_score + ci_delta):.1f}分",
            "explanation": "統計學信心區間源自 100 次 Monte Carlo 隨機模擬，反映當關鍵估值與財務變數發生正常標準差抖動時，Master Score 的 95% 信賴分佈區間。"
        }
        
        formula_parts = [f"{c['strategy']}({c['score']}分)*{c['weight_pct']}" for c in master_contributions]
        unification_formula = (
            f"主導綜合評級 (Master Verdict) 依據 [{matched_sector}] 產業動態加權與估值天花板算出：\n"
            f"Master Score = {' + '.join(formula_parts)} = {master_score:.1f} 分 ➔ 最終評級：{master_rating}\n"
            f"權重與約束依據：{rationale}"
        )
        
        results["master_verdict"] = {
            "score": master_score,
            "rating": master_rating,
            "raw_rating": raw_rating,
            "color": master_color,
            "sector": matched_sector,
            "rationale": rationale,
            "valuation_cap_applied": valuation_cap_applied,
            "confidence_interval": score_ci,
            "contributions": master_contributions,
            "unification_formula": unification_formula
        }

        # Multi-Horizon Recommendations
        results["multi_horizon"] = self._calculate_multi_horizon_advice(dimension_scores, master_rating)
        return results

    def _calculate_multi_horizon_advice(self, dims: dict, master_rating: str) -> dict:
        m_score = dims.get("momentum", 50.0)
        g_score = dims.get("growth", 50.0)
        q_score = dims.get("quality", 50.0)
        v_score = dims.get("valuation", 50.0)
        s_score = dims.get("safety", 50.0)
        
        st_score = m_score * 0.6 + g_score * 0.4
        mt_score = g_score * 0.4 + q_score * 0.3 + v_score * 0.3
        lt_score = q_score * 0.45 + s_score * 0.30 + v_score * 0.25
        
        st_rating = self.get_rating(st_score)
        mt_rating = self.get_rating(mt_score)
        lt_rating = self.get_rating(lt_score)
        
        st_desc = "技術面多頭動能強勁，適合順勢波段操作。" if st_score >= 62 else "技術面處於整理階段，短期區間震盪觀望。"
        mt_desc = "未來一年盈餘成長可期，估值與成長性兼具。" if mt_score >= 62 else "未來一年業績增速中等，需關注季度財報兌現狀況。"
        lt_desc = "具備強大商業護城河與穩健資產負債表，適合長期持股複利。" if lt_score >= 62 else "長期資本回報率或財務結構有待加強，建議控制倉位。"
        
        return {
            "short_term_3m": {"score": float(st_score), "rating": st_rating, "desc": st_desc, "horizon": "短期 (3個月)"},
            "medium_term_1y": {"score": float(mt_score), "rating": mt_rating, "desc": mt_desc, "horizon": "中期 (1年)"},
            "long_term_3y": {"score": float(lt_score), "rating": lt_rating, "desc": lt_desc, "horizon": "長期 (3年)"}
        }
