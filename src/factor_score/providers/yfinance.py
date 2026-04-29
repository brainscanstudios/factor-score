import logging
import pandas as pd

log = logging.getLogger(__name__)


class YFinanceProvider:
    """Default data provider backed by yfinance (optional dependency)."""

    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance is required for YFinanceProvider. "
                "Install it with: pip install 'factor-score[yfinance]'"
            )

        try:
            df = yf.Ticker(ticker).history(period=period)
            if df.empty:
                log.warning("No history returned for %s", ticker)
            return df
        except Exception as exc:
            log.warning("Failed to fetch history for %s: %s", ticker, exc)
            return pd.DataFrame()
