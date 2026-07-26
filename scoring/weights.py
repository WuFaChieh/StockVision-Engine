# Default feature weights for evidence fusion
# The Learning Layer can optimize these values based on historical performance.

FEATURE_WEIGHTS = {
    "growth": {
        "revenue_growth_yoy": 0.30,
        "revenue_cagr_3y": 0.30,
        "eps_growth_yoy": 0.20,
        "fcf_growth_yoy": 0.20
    },
    "quality": {
        "roe": 0.40,
        "roic": 0.20,
        "gross_margin": 0.15,
        "operating_margin": 0.15,
        "gross_margin_trend": 0.10
    },
    "safety": {
        "debt_to_equity": 0.35,
        "current_ratio": 0.25,
        "interest_coverage": 0.25,
        "inventory_turnover": 0.15
    },
    "valuation": {
        "pe_percentile": 0.25,
        "pb_percentile": 0.25,
        "peg": 0.25,
        "dcf_premium": 0.25
    },
    "momentum": {
        "rsi": 0.20,
        "macd_hist": 0.20,
        "distance_ma50": 0.20,
        "distance_ma200": 0.15,
        "ma_alignment": 0.15,
        "volatility": 0.10
    }
}
