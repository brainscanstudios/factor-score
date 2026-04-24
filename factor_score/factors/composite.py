import pandas as pd

from ..models import FactorConfig, FactorScore
from .momentum import compute_momentum, compute_volatility, compute_vol_adjusted_momentum
from .value import compute_relative_value


def compute_raw_factors(
    histories: dict[str, pd.DataFrame], config: FactorConfig
) -> list[dict]:
    records = []
    for ticker, df in histories.items():
        if df.empty:
            continue
        records.append({
            "ticker": ticker,
            "momentum_90d": compute_momentum(df, config.momentum_short_days),
            "momentum_180d": compute_momentum(df, config.momentum_long_days),
            "vol_adj_momentum": compute_vol_adjusted_momentum(df, config.momentum_short_days),
            "relative_value": compute_relative_value(df),
            "volatility": compute_volatility(df, config.volatility_days),
        })
    return records


def _normalize_ranks(series: pd.Series, ascending: bool = True) -> pd.Series:
    """Rank a series and normalize to [0, 1]. NaN values are held at 0.5 (neutral)."""
    ranks = series.rank(ascending=ascending, na_option="keep")
    n = ranks.notna().sum()
    if n <= 1:
        return pd.Series(0.5, index=series.index)
    normalized = (ranks - 1) / (n - 1)
    return normalized.fillna(0.5)


def build_composite(
    records: list[dict], config: FactorConfig, as_of: str
) -> list[FactorScore]:
    """Normalize ranks within the universe and compute composite scores."""
    if not records:
        return []

    df = pd.DataFrame(records).set_index("ticker")

    # relative_value: ascending=False because proximity to 52w-low is more attractive
    df["s_mom_short"]   = _normalize_ranks(df["momentum_90d"],     ascending=True)
    df["s_mom_long"]    = _normalize_ranks(df["momentum_180d"],    ascending=True)
    df["s_vol_adj_mom"] = _normalize_ranks(df["vol_adj_momentum"], ascending=True)
    df["s_rel_value"]   = _normalize_ranks(df["relative_value"],   ascending=False)

    df["composite_score"] = (
        df["s_mom_short"]   * config.weight_momentum_short +
        df["s_mom_long"]    * config.weight_momentum_long +
        df["s_vol_adj_mom"] * config.weight_vol_adj_momentum +
        df["s_rel_value"]   * config.weight_relative_value
    )
    df["composite_rank"] = (
        df["composite_score"].rank(ascending=False, na_option="bottom").astype(int)
    )
    df = df.sort_values("composite_score", ascending=False)

    return [
        FactorScore(
            ticker=ticker,
            as_of=as_of,
            momentum_90d=row["momentum_90d"],
            momentum_180d=row["momentum_180d"],
            vol_adj_momentum=row["vol_adj_momentum"],
            relative_value=row["relative_value"],
            volatility=row["volatility"],
            score_momentum_short=row["s_mom_short"],
            score_momentum_long=row["s_mom_long"],
            score_vol_adj_momentum=row["s_vol_adj_mom"],
            score_relative_value=row["s_rel_value"],
            composite_score=row["composite_score"],
            composite_rank=int(row["composite_rank"]),
        )
        for ticker, row in df.iterrows()
    ]
