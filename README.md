# factor-score

Quantitative factor scoring for equities and ETFs.

```python
from factor_score import FactorEngine

engine = FactorEngine()
scores = engine.score(["SCHD", "VGT", "XLE", "HDEF"])
for s in scores:
    print(f"{s.ticker:6}  composite={s.composite_score:.2f}  rank=#{s.composite_rank}")
```

## Install

```bash
pip install factor-score           # core (bring your own data)
pip install 'factor-score[yfinance]'  # with built-in yfinance provider
```

## Design

- **Input-agnostic**: implement the two-method `DataProvider` protocol to plug in any data source (yfinance, Polygon, IBKR, CSV).
- **Code-driven config**: use `FactorConfig` to override weights and lookback periods — no YAML required.
- **Normalized scores**: composite scores are 0–1 within the scored universe; raw factor values are always returned alongside.

## Factors

| Factor | Weight | Description |
|---|---|---|
| Vol-adjusted momentum | 35% | 90d return / annualized vol — rewards smooth trends |
| Momentum (90d) | 25% | Trailing 90-day return |
| Momentum (180d) | 25% | Trailing 180-day return |
| Relative value | 15% | Proximity to 52-week low (mean-reversion tilt) |

## Custom config

```python
from factor_score import FactorEngine, FactorConfig

config = FactorConfig(
    weight_vol_adj_momentum=0.50,
    weight_momentum_short=0.25,
    weight_momentum_long=0.15,
    weight_relative_value=0.10,
    momentum_short_days=60,
)
engine = FactorEngine(config=config)
```

## Custom data provider

```python
import pandas as pd
from factor_score import FactorEngine

class MyProvider:
    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        # return a DataFrame with a "Close" column
        ...

engine = FactorEngine(provider=MyProvider())
```

## License

MIT
