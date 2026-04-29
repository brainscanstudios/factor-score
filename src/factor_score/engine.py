import logging
from datetime import datetime, timezone

from .factors.composite import build_composite, compute_raw_factors
from .models import FactorConfig, FactorScore
from .providers.base import DataProvider

log = logging.getLogger(__name__)


class FactorEngine:
    """
    Score a universe of tickers across quantitative factor dimensions.

    Parameters
    ----------
    config : FactorConfig, optional
        Factor weights and lookback settings. Defaults to library defaults.
    provider : DataProvider, optional
        Market data source. Defaults to YFinanceProvider (requires yfinance).

    Examples
    --------
    >>> from factor_score import FactorEngine
    >>> engine = FactorEngine()
    >>> scores = engine.score(["DIS", "NVDA", "MSFT", "META"])
    >>> scores[0].ticker, scores[0].composite_score
    ('NVDA', 0.83)
    """

    def __init__(
        self,
        config: FactorConfig | None = None,
        provider: DataProvider | None = None,
    ) -> None:
        self.config = config or FactorConfig()
        if provider is None:
            from .providers.yfinance import YFinanceProvider
            provider = YFinanceProvider()
        self.provider = provider

    def score(
        self,
        tickers: list[str] | str,
        as_of: str | None = None,
    ) -> list[FactorScore]:
        """
        Score one or more tickers within their peer universe.

        Composite scores (0–1) are normalized relative to the provided universe.
        Passing a single ticker returns raw factor values only — composite_score
        and composite_rank will be None since there is no peer universe to rank against.

        Parameters
        ----------
        tickers : str or list[str]
            Ticker(s) to score.
        as_of : str, optional
            ISO date label stamped on results (metadata only; data is always fetched live).

        Returns
        -------
        list[FactorScore]
            Sorted descending by composite_score (best candidate first).
        """
        if isinstance(tickers, str):
            tickers = [tickers]
        tickers = [t.upper() for t in tickers]
        as_of = as_of or datetime.now(timezone.utc).date().isoformat()

        log.info("Scoring %d ticker(s): %s", len(tickers), tickers)
        histories = {
            t: self.provider.get_history(t, period=self.config.history_period)
            for t in tickers
        }

        records = compute_raw_factors(histories, self.config)

        if len(records) < 2:
            if not records:
                return []
            r = records[0]
            return [
                FactorScore(
                    ticker=r["ticker"],
                    as_of=as_of,
                    momentum_90d=r["momentum_90d"],
                    momentum_180d=r["momentum_180d"],
                    vol_adj_momentum=r["vol_adj_momentum"],
                    relative_value=r["relative_value"],
                    volatility=r["volatility"],
                )
            ]

        return build_composite(records, self.config, as_of)

    def top(
        self,
        tickers: list[str],
        n: int = 3,
        as_of: str | None = None,
    ) -> list[FactorScore]:
        """Return the top N tickers by composite score."""
        return self.score(tickers, as_of=as_of)[:n]
