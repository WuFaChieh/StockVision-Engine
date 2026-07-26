class IndustryAnalyzer:
    """
    Classifies companies by industry, provides sector-specific benchmarks, 
    and returns dynamic sector-specific dimension weights.
    """
    
    BENCHMARKS = {
        "Technology": {
            "roe": 0.15,
            "debt_to_equity": 0.5,
            "current_ratio": 1.5,
            "pe": 25.0,
            "pb": 3.0
        },
        "Financials": {
            "roe": 0.08,
            "debt_to_equity": 5.0,
            "current_ratio": 1.0,
            "pe": 12.0,
            "pb": 1.0
        },
        "Utilities": {
            "roe": 0.06,
            "debt_to_equity": 1.5,
            "current_ratio": 1.0,
            "pe": 15.0,
            "pb": 1.2
        },
        "Transportation": {
            "roe": 0.10,
            "debt_to_equity": 1.0,
            "current_ratio": 1.2,
            "pe": 10.0,
            "pb": 1.5
        },
        "Default": {
            "roe": 0.10,
            "debt_to_equity": 0.8,
            "current_ratio": 1.2,
            "pe": 15.0,
            "pb": 1.5
        }
    }

    # Dynamic Sector Weights for 5 Capability Dimensions
    DYNAMIC_SECTOR_WEIGHTS = {
        "Technology": {
            "growth": 0.35,
            "valuation": 0.25,
            "quality": 0.20,
            "momentum": 0.15,
            "safety": 0.05
        },
        "Financials": {
            "safety": 0.35,
            "quality": 0.30,
            "valuation": 0.20,
            "growth": 0.10,
            "momentum": 0.05
        },
        "Utilities": {
            "safety": 0.40,
            "quality": 0.30,
            "valuation": 0.20,
            "growth": 0.05,
            "momentum": 0.05
        },
        "Transportation": {
            "valuation": 0.30,
            "safety": 0.25,
            "quality": 0.20,
            "momentum": 0.15,
            "growth": 0.10
        },
        "Default": {
            "quality": 0.25,
            "safety": 0.25,
            "valuation": 0.20,
            "growth": 0.20,
            "momentum": 0.10
        }
    }

    def __init__(self, processed_data: dict):
        self.ticker = processed_data.get("ticker", "")
        self.info = processed_data.get("info", {})

    def analyze(self) -> dict:
        """
        Classifies stock, returns benchmarks, and dynamic industry weights.
        """
        sector = self.info.get("sector", "Default")
        
        matched_sector = "Default"
        if sector in self.BENCHMARKS:
            matched_sector = sector
        elif sector in ["Technology", "Electronic Technology", "Technology Services", "Consumer Electronics", "Software", "Semiconductors"]:
            matched_sector = "Technology"
        elif sector in ["Financials", "Finance", "Financial Services", "Banking", "Insurance"]:
            matched_sector = "Financials"
        elif sector in ["Utilities", "Infrastructure", "Telecommunications", "Public Utilities"]:
            matched_sector = "Utilities"
        elif sector in ["Transportation", "Shipping", "Marine Shipping", "Logistics", "Services"]:
            matched_sector = "Transportation"
            
        benchmarks = self.BENCHMARKS[matched_sector]
        sector_weights = self.DYNAMIC_SECTOR_WEIGHTS[matched_sector]
        
        return {
            "sector": sector,
            "industry": self.info.get("industry", "Unknown"),
            "matched_sector": matched_sector,
            "benchmarks": benchmarks,
            "sector_weights": sector_weights
        }