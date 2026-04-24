import numpy as np
import pandas as pd


def compute_momentum(df: pd.DataFrame, days: int) -> float | None:
    """Trailing return over N trading days."""
    if len(df) < days:
        return None
    return float((df["Close"].iloc[-1] / df["Close"].iloc[-days]) - 1)


def compute_volatility(df: pd.DataFrame, days: int = 20) -> float | None:
    """Annualized volatility over the last N trading days."""
    returns = df["Close"].pct_change().dropna()
    if len(returns) < days:
        return None
    return float(returns.iloc[-days:].std() * np.sqrt(252))


def compute_vol_adjusted_momentum(df: pd.DataFrame, days: int = 90) -> float | None:
    """Momentum / annualized volatility — rewards smooth, low-noise trends."""
    mom = compute_momentum(df, days)
    vol = compute_volatility(df, days)
    if mom is None or vol is None or vol == 0:
        return None
    return mom / vol
