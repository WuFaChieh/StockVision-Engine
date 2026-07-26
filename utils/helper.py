"""
Common mathematical and formatting helper functions for StockVision Pro.
"""

import pandas as pd
import numpy as np

def safe_divide(numerator, denominator, default: float = 0.0):
    """
    Safely divides two numbers, Series, or arrays, handling zero, NaN, and Inf.
    """
    if isinstance(numerator, (pd.Series, np.ndarray)) or isinstance(denominator, (pd.Series, np.ndarray)):
        num = np.asarray(numerator, dtype=float)
        den = np.asarray(denominator, dtype=float)
        with np.errstate(divide='ignore', invalid='ignore'):
            res = np.where((den != 0) & ~np.isnan(den) & ~np.isinf(den), num / den, default)
            res = np.where(np.isnan(res) | np.isinf(res), default, res)
        if isinstance(numerator, pd.Series):
            return pd.Series(res, index=numerator.index)
        elif isinstance(denominator, pd.Series):
            return pd.Series(res, index=denominator.index)
        return res
    else:
        if denominator is None or numerator is None:
            return default
        try:
            num = float(numerator)
            den = float(denominator)
            if den == 0 or np.isnan(num) or np.isnan(den) or np.isinf(num) or np.isinf(den):
                return default
            res = num / den
            if np.isnan(res) or np.isinf(res):
                return default
            return res
        except (ValueError, TypeError, ZeroDivisionError):
            return default

def clamp(val: float, min_val: float, max_val: float) -> float:
    """
    Clamps a scalar value to be within [min_val, max_val].
    """
    if val is None or np.isnan(val):
        return min_val
    return max(min_val, min(max_val, float(val)))

def format_percentage(val: float, precision: int = 2) -> str:
    """
    Formats decimal value (0.152) as percentage string ('15.20%').
    """
    if val is None or np.isnan(val):
        return "N/A"
    return f"{val * 100:.{precision}f}%"

def format_currency(val: float) -> str:
    """
    Formats large currency numbers (e.g. 1,000,000,000).
    """
    if val is None or np.isnan(val):
        return "N/A"
    if abs(val) >= 1e12:
        return f"${val / 1e12:.2f}T"
    elif abs(val) >= 1e9:
        return f"${val / 1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"${val / 1e6:.2f}M"
    else:
        return f"${val:,.2f}"
