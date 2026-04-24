import numpy as np
import pandas as pd
import pytest

from factor_score.factors.momentum import (
    compute_momentum,
    compute_volatility,
    compute_vol_adjusted_momentum,
)
from factor_score.factors.value import compute_relative_value


def _make_df(prices: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"Close": prices})


class TestComputeMomentum:
    def test_basic_gain(self):
        # 91 prices: iloc[-1]=91, iloc[-90]=2 → 91/2 - 1 = 44.5
        prices = list(range(1, 92))
        result = compute_momentum(_make_df(prices), 90)
        assert result == pytest.approx(44.5)

    def test_insufficient_history_returns_none(self):
        assert compute_momentum(_make_df([1.0, 2.0]), 90) is None

    def test_flat_prices_return_zero(self):
        prices = [100.0] * 91
        assert compute_momentum(_make_df(prices), 90) == pytest.approx(0.0)


class TestComputeVolatility:
    def test_zero_vol_flat_prices(self):
        prices = [100.0] * 25
        assert compute_volatility(_make_df(prices), 20) == pytest.approx(0.0)

    def test_insufficient_history_returns_none(self):
        assert compute_volatility(_make_df([1.0, 2.0]), 20) is None

    def test_positive_for_noisy_series(self):
        rng = np.random.default_rng(42)
        prices = (1 + rng.normal(0, 0.01, 25)).cumprod() * 100
        vol = compute_volatility(_make_df(prices.tolist()), 20)
        assert vol is not None and vol > 0


class TestComputeVolAdjustedMomentum:
    def test_returns_none_when_vol_is_zero(self):
        prices = [100.0] * 91
        assert compute_vol_adjusted_momentum(_make_df(prices), 90) is None

    def test_sign_matches_momentum(self):
        prices = list(range(50, 142))  # uptrend
        result = compute_vol_adjusted_momentum(_make_df(prices), 90)
        assert result is not None and result > 0


class TestComputeRelativeValue:
    def test_at_high_returns_one(self):
        prices = list(range(1, 11))  # current = 10 = max
        assert compute_relative_value(_make_df(prices)) == pytest.approx(1.0)

    def test_at_low_returns_zero(self):
        prices = list(range(10, 0, -1))  # current = 1 = min
        assert compute_relative_value(_make_df(prices)) == pytest.approx(0.0)

    def test_midpoint(self):
        prices = [1.0, 3.0, 2.0]  # current=2, low=1, high=3 → 0.5
        assert compute_relative_value(_make_df(prices)) == pytest.approx(0.5)

    def test_flat_returns_none(self):
        prices = [5.0] * 10
        assert compute_relative_value(_make_df(prices)) is None
