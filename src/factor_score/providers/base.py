from typing import Protocol, runtime_checkable
import pandas as pd


@runtime_checkable
class DataProvider(Protocol):
    """
    Protocol for market data providers.

    Implement this to plug in any data source (Polygon, IBKR, CSV, etc.).
    The engine calls get_history() for each ticker during scoring.
    """

    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        Return OHLCV price history for a ticker.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. "NVDA").
        period : str
            Lookback window (e.g. "1y", "2y"). Interpretation is provider-defined.

        Returns
        -------
        pd.DataFrame
            Must contain a "Close" column. Index should be a DatetimeIndex.
            Return an empty DataFrame if data is unavailable rather than raising.
        """
        ...
