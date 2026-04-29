import pandas as pd


def compute_relative_value(df: pd.DataFrame) -> float | None:
    """
    Position within the 52-week price range.

    Returns 0.0 at the 52-week low (most attractive for mean-reversion)
    and 1.0 at the 52-week high. Used with an inverted rank in the composite
    so lower price position scores higher.
    """
    lookback = df["Close"].iloc[-252:] if len(df) >= 252 else df["Close"]
    high_52 = lookback.max()
    low_52 = lookback.min()
    current = df["Close"].iloc[-1]
    if high_52 == low_52:
        return None
    return float((current - low_52) / (high_52 - low_52))
