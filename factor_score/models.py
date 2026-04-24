from dataclasses import dataclass
from typing import Optional


@dataclass
class FactorConfig:
    """Weights and lookback settings for composite factor scoring."""

    # Lookback periods (trading days)
    momentum_short_days: int = 90
    momentum_long_days: int = 180
    volatility_days: int = 20

    # Composite weights — must sum to 1.0
    weight_momentum_short: float = 0.25
    weight_momentum_long: float = 0.25
    weight_vol_adj_momentum: float = 0.35
    weight_relative_value: float = 0.15

    # History window passed to the data provider
    history_period: str = "1y"

    def __post_init__(self) -> None:
        total = (
            self.weight_momentum_short
            + self.weight_momentum_long
            + self.weight_vol_adj_momentum
            + self.weight_relative_value
        )
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Factor weights must sum to 1.0, got {total:.4f}")


@dataclass
class FactorScore:
    """Factor scores for a single ticker, produced by FactorEngine.score()."""

    ticker: str
    as_of: str

    # Raw computed values
    momentum_90d: Optional[float] = None
    momentum_180d: Optional[float] = None
    vol_adj_momentum: Optional[float] = None
    relative_value: Optional[float] = None
    volatility: Optional[float] = None

    # Normalized 0–1 scores within the scored universe (None for single-ticker calls)
    score_momentum_short: Optional[float] = None
    score_momentum_long: Optional[float] = None
    score_vol_adj_momentum: Optional[float] = None
    score_relative_value: Optional[float] = None

    # Composite (0–1, higher = more favorable); None for single-ticker calls
    composite_score: Optional[float] = None
    composite_rank: Optional[int] = None
