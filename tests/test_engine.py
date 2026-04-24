import pandas as pd
import pytest

from factor_score import FactorConfig, FactorEngine, FactorScore


def _make_history(prices: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"Close": prices})


class StubProvider:
    """Deterministic in-memory provider for testing."""

    def __init__(self, histories: dict[str, list[float]]):
        self._histories = histories

    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        prices = self._histories.get(ticker, [])
        return _make_history(prices)


def _uptrend(n: int = 252, start: float = 100.0, slope: float = 0.3) -> list[float]:
    return [start + i * slope for i in range(n)]


def _downtrend(n: int = 252, start: float = 130.0, slope: float = -0.3) -> list[float]:
    return [start + i * slope for i in range(n)]


class TestFactorEngineScore:
    def test_returns_list_of_factor_scores(self):
        provider = StubProvider({"NVDA": _uptrend(), "MSFT": _downtrend()})
        engine = FactorEngine(provider=provider)
        results = engine.score(["NVDA", "MSFT"])
        assert len(results) == 2
        assert all(isinstance(r, FactorScore) for r in results)

    def test_sorted_descending_by_composite(self):
        provider = StubProvider({"NVDA": _uptrend(), "MSFT": _downtrend()})
        engine = FactorEngine(provider=provider)
        results = engine.score(["NVDA", "MSFT"])
        scores = [r.composite_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_single_ticker_returns_raw_only(self):
        provider = StubProvider({"NVDA": _uptrend()})
        engine = FactorEngine(provider=provider)
        results = engine.score("NVDA")
        assert len(results) == 1
        assert results[0].composite_score is None
        assert results[0].composite_rank is None
        assert results[0].momentum_90d is not None

    def test_uptrend_beats_downtrend(self):
        provider = StubProvider({"UP": _uptrend(), "DOWN": _downtrend()})
        engine = FactorEngine(provider=provider)
        results = engine.score(["UP", "DOWN"])
        assert results[0].ticker == "UP"

    def test_tickers_are_uppercased(self):
        provider = StubProvider({"NVDA": _uptrend()})
        engine = FactorEngine(provider=provider)
        results = engine.score(["schd"])
        assert results[0].ticker == "NVDA"

    def test_empty_history_ticker_is_skipped(self):
        provider = StubProvider({"NVDA": _uptrend(), "GHOST": []})
        engine = FactorEngine(provider=provider)
        results = engine.score(["NVDA", "GHOST"])
        tickers = [r.ticker for r in results]
        assert "GHOST" not in tickers

    def test_composite_scores_between_zero_and_one(self):
        provider = StubProvider({
            "A": _uptrend(slope=0.5),
            "B": _uptrend(slope=0.2),
            "C": _downtrend(),
        })
        engine = FactorEngine(provider=provider)
        results = engine.score(["A", "B", "C"])
        for r in results:
            assert 0.0 <= r.composite_score <= 1.0

    def test_ranks_are_sequential(self):
        provider = StubProvider({
            "A": _uptrend(slope=0.5),
            "B": _uptrend(slope=0.2),
            "C": _downtrend(),
        })
        engine = FactorEngine(provider=provider)
        results = engine.score(["A", "B", "C"])
        ranks = sorted(r.composite_rank for r in results)
        assert ranks == [1, 2, 3]


class TestFactorConfig:
    def test_default_weights_sum_to_one(self):
        cfg = FactorConfig()
        total = (cfg.weight_momentum_short + cfg.weight_momentum_long +
                 cfg.weight_vol_adj_momentum + cfg.weight_relative_value)
        assert abs(total - 1.0) < 1e-9

    def test_invalid_weights_raise(self):
        with pytest.raises(ValueError, match="sum to 1.0"):
            FactorConfig(weight_momentum_short=0.5, weight_momentum_long=0.5,
                         weight_vol_adj_momentum=0.5, weight_relative_value=0.5)


class TestFactorEngineTop:
    def test_top_returns_n_results(self):
        provider = StubProvider({
            "A": _uptrend(slope=0.5),
            "B": _uptrend(slope=0.3),
            "C": _uptrend(slope=0.1),
            "D": _downtrend(),
        })
        engine = FactorEngine(provider=provider)
        results = engine.top(["A", "B", "C", "D"], n=2)
        assert len(results) == 2
