class FinancialKnowledgeBase:
    """
    Decouples financial knowledge and explanations from procedural logic.
    Defines metric metadata, interpretations, and benchmarking rules.
    """
    
    METRIC_INFO = {
        # Growth
        "revenue_growth_yoy": {
            "name": "營收年增率 (YoY)",
            "desc": "最新月份營業收入與去年同期相比的成長幅度，反映公司短期業務擴張速度。",
            "good_direction": "high"
        },
        "revenue_cagr_3y": {
            "name": "三年營收年複合成長率 (CAGR)",
            "desc": "過去三年營收的年複合增長率，反映公司中長期的成長動能與擴張穩定性。",
            "good_direction": "high"
        },
        "eps_growth_yoy": {
            "name": "EPS年增率 (YoY)",
            "desc": "每股盈餘 (EPS) 相較於去年同期的成長率，代表企業為股東創造淨利潤的成長能力。",
            "good_direction": "high"
        },
        "fcf_growth_yoy": {
            "name": "自由現金流年增率 (YoY)",
            "desc": "自由現金流 (FCF) 相較於去年同期的成長率，是企業真實盈餘成長的硬指標。",
            "good_direction": "high"
        },
        
        # Quality
        "roe": {
            "name": "股東權益報酬率 (ROE)",
            "desc": "企業利用股東資金創造獲利的效率，也是衡量企業品質的核心指標。",
            "good_direction": "high"
        },
        "roic": {
            "name": "投入資本回報率 (ROIC)",
            "desc": "企業利用所有投入資本（含股東權益與有息負債）創造利潤的效率，可排除財務槓桿的干擾。",
            "good_direction": "high"
        },
        "gross_margin": {
            "name": "毛利率",
            "desc": "銷售收入扣除銷貨成本後的利潤率，反映產品競爭力、定價權與技術門檻。",
            "good_direction": "high"
        },
        "operating_margin": {
            "name": "營業利益率",
            "desc": "營業利益佔營收的比率，反映公司本業經營管理與控制營業費用的能力。",
            "good_direction": "high"
        },
        "gross_margin_trend": {
            "name": "毛利率趨勢",
            "desc": "最新毛利率與過去幾季均值的差值，反映利潤率是否持續改善或惡化。",
            "good_direction": "high"
        },
        "piotroski_f_score": {
            "name": "Piotroski F-Score 點數",
            "desc": "史丹佛學者 Piotroski 提出的 0-9 點財務健康度指標，高分代表財務全面轉強。",
            "good_direction": "high"
        },
        "altman_z_score": {
            "name": "Altman Z-Score",
            "desc": "紐約大學教授 Altman 提出的破產預警模型。>2.99 為安全區，<1.81 為財務高風險區。",
            "good_direction": "high"
        },
        
        # Safety
        "debt_to_equity": {
            "name": "負債權益比 (D/E Ratio)",
            "desc": "總負債相較於股東權益的比率，衡量企業財務槓桿的高低與長期償債風險。",
            "good_direction": "low"
        },
        "current_ratio": {
            "name": "流動比率",
            "desc": "流動資產除以流動負債，反映公司一年內償還短期債務的能力（一般以高於1.5或1.0為安全）。",
            "good_direction": "high"
        },
        "interest_coverage": {
            "name": "利息保障倍數",
            "desc": "營業利益除以利息費用，衡量本業獲利支付借款利息的能力，低於2倍通常具高度財務風險。",
            "good_direction": "high"
        },
        "inventory_turnover": {
            "name": "存貨週轉率",
            "desc": "銷貨成本與存貨的比率，反映公司銷貨速度與存貨管理效率，過低可能代表存貨積壓。",
            "good_direction": "high"
        },
        
        # Valuation
        "pe": {
            "name": "本益比 (PE)",
            "desc": "當前股價除以每股盈餘，反映市場願意為公司每元獲利支付的溢價。",
            "good_direction": "low"
        },
        "pb": {
            "name": "股價淨值比 (PB)",
            "desc": "當前股價除以每股淨值，常用於評估資產密集型或金融業的估值高低。",
            "good_direction": "low"
        },
        "pe_percentile": {
            "name": "本益比歷史百分位",
            "desc": "目前本益比在歷史波動區間中所處的位置，百分位越低代表估值相對歷史均值越便宜。",
            "good_direction": "low"
        },
        "pb_percentile": {
            "name": "股價淨值比歷史百分位",
            "desc": "目前股價淨值比在歷史區間中所處的位置，百分位越低代表當前資產溢價低於歷史平均。",
            "good_direction": "low"
        },
        "peg": {
            "name": "PEG 比例",
            "desc": "本益比除以盈餘成長率，將成長因素納入估值考量。PEG < 1 通常被視為低估且具備高成長性。",
            "good_direction": "low"
        },
        "dcf_premium": {
            "name": "DCF 溢價率",
            "desc": "當前市價較折現現金流 (DCF) 模型估計之內在價值的溢價程度。負值代表股價低於合理價 (折價)。",
            "good_direction": "low"
        },
        "ev_ebitda": {
            "name": "EV/EBITDA 倍數",
            "desc": "企業價值對息稅折舊攤銷前利潤的倍數，能排除資本結構與稅率差異干擾。",
            "good_direction": "low"
        },
        "ev_sales": {
            "name": "EV/Sales 倍數",
            "desc": "企業價值對營業收入的比率，常用於評估微利或高成長科技股的估值。",
            "good_direction": "low"
        },
        
        # Momentum
        "rsi": {
            "name": "相對強弱指標 (RSI)",
            "desc": "衡量股價買賣盤動能。RSI > 70 屬超買區，RSI < 30 屬超賣區，50 附近代表動能平穩。",
            "good_direction": "neutral"
        },
        "macd_hist": {
            "name": "MACD 柱狀值佔比",
            "desc": "MACD柱狀值佔股價比率，反映短期價格趨勢動能的擴張或收斂。",
            "good_direction": "high"
        },
        "distance_ma50": {
            "name": "50日均線乖離率",
            "desc": "股價與50日移動平均線的距離比例，反映中期趨勢是強勢還是修正。",
            "good_direction": "high"
        },
        "distance_ma200": {
            "name": "200日均線乖離率",
            "desc": "股價與200日均線的距離比例，反映長線牛熊分界與均線支撐或壓力的遠近。",
            "good_direction": "high"
        },
        "ma_alignment": {
            "name": "均線排列多頭評分",
            "desc": "基於多條均線排列的得分，均線呈現完美多頭排列 (Close > MA20 > MA50 > MA200) 時得分最高。",
            "good_direction": "high"
        },
        "volatility": {
            "name": "年化波動率",
            "desc": "衡量過去30個交易日的股價波動劇烈程度。波動過高通常伴隨較高投資風險，但也代表動能劇烈。",
            "good_direction": "low"
        }
    }

    @classmethod
    def get_explanation(cls, metric: str, val: float, benchmark: float = None) -> str:
        """
        Translates a metric's numeric value and benchmark into a financial reason.
        """
        info = cls.METRIC_INFO.get(metric)
        if not info:
            return f"數值為 {val:.2f}。"
            
        name = info["name"]
        val_pct = val * 100
        bench_pct = (benchmark * 100) if benchmark is not None else None
        
        if metric == "piotroski_f_score":
            val_int = int(val)
            if val_int >= 7:
                return f"Piotroski F-Score 高達 {val_int}/9 分，顯示獲利能力、資產負債表與營運效率呈現全面性好轉。"
            elif val_int >= 5:
                return f"Piotroski F-Score 為 {val_int}/9 分，財務體質維持在正常平穩水準。"
            else:
                return f"Piotroski F-Score 僅有 {val_int}/9 分，代表財務基本面出現警訊，營運效率有所衰退。"

        elif metric == "altman_z_score":
            if val >= 2.99:
                return f"Altman Z-Score 為 {val:.2f}（處於 Safe 區域），企業幾乎無短期財務違約或破產風險。"
            elif val >= 1.81:
                return f"Altman Z-Score 為 {val:.2f}（處於 Grey 區域），財務安全處於中立過渡帶，需密切注意流動性。"
            else:
                return f"Altman Z-Score 僅為 {val:.2f}（處於 Distress 警訊區），代表財務結構面臨較高風險。"

        elif metric == "roe":
            if val <= 0:
                return f"企業股東權益報酬率為負值（{val_pct:.2f}%），代表本期虧損，資本效率不佳。"
            if benchmark:
                if val >= benchmark * 1.5:
                    return f"股東權益報酬率高達 {val_pct:.2f}%，遠超產業基準（{bench_pct:.2f}%），代表資本使用效率極其優秀。"
                elif val >= benchmark:
                    return f"股東權益報酬率為 {val_pct:.2f}%，高於產業平均基準（{bench_pct:.2f}%），表現穩健。"
                else:
                    return f"股東權益報酬率為 {val_pct:.2f}%，低於產業平均基準（{bench_pct:.2f}%），資本回報率有待提升。"
            return f"股東權益報酬率為 {val_pct:.2f}%，代表每百元股東權益可創造 {val_pct:.2f} 元淨利。"
            
        elif metric == "debt_to_equity":
            if val == 0:
                return "無有息負債，財務結構極度安全，但缺乏財務槓桿效應。"
            if benchmark:
                if val <= benchmark * 0.5:
                    return f"負債權益比為 {val_pct:.2f}%，遠低於產業平均安全閥值（{bench_pct:.2f}%），財務體質極度穩健。"
                elif val <= benchmark:
                    return f"負債權益比為 {val_pct:.2f}%，低於產業基準值（{bench_pct:.2f}%），財務風險在安全範圍內。"
                else:
                    return f"負債權益比高達 {val_pct:.2f}%，已超出該產業平均基準值（{bench_pct:.2f}%），需警戒財務槓桿與債務償還風險。"
            return f"負債權益比為 {val_pct:.2f}%，反映資產負債表槓桿程度。"
            
        elif metric == "revenue_growth_yoy":
            if val > 0.2:
                return f"月營收年增率高達 {val_pct:.2f}%，業務呈現爆發性成長。"
            elif val > 0.05:
                return f"月營收年增率為 {val_pct:.2f}%，業務維持健康擴張趨勢。"
            elif val > -0.05:
                return f"月營收年增率為 {val_pct:.2f}%，業務規模持平，成長面臨瓶頸。"
            else:
                return f"月營收年增率衰退 {abs(val_pct):.2f}%，需注意市場需求下滑或競爭力流失。"

        elif metric == "ev_ebitda":
            if val < 8.0:
                return f"EV/EBITDA僅為 {val:.1f}x，估值相當便宜（低於市場常態）。"
            elif val < 15.0:
                return f"EV/EBITDA為 {val:.1f}x，估值處於合理區間。"
            else:
                return f"EV/EBITDA高達 {val:.1f}x，市場已給予較高之營運溢價。"

        # Default fallback
        dir_good = info["good_direction"]
        if dir_good == "high":
            if val > (benchmark or 0):
                return f"{name} 為 {val:.2f}，表現優於標準。"
            else:
                return f"{name} 為 {val:.2f}，表現低於預期。"
        elif dir_good == "low":
            if val < (benchmark or 9999):
                return f"{name} 為 {val:.2f}，風險控制良好。"
            else:
                return f"{name} 為 {val:.2f}，指標偏高，需多加留意。"
                
        return f"{name} 的數值為 {val:.2f}。"
