# factor-score

Quantitative factor scoring for equities and ETFs.

```python
from factor_score import FactorEngine

engine = FactorEngine()
scores = engine.score(["DIS", "NVDA", "MSFT", "META"])
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

## Contributing

### Local development setup

**Prerequisites:** Python 3.11 or 3.12, and [pip](https://pip.pypa.io/).

1. Clone the repo and create a virtual environment:

```bash
git clone https://github.com/brainscanstudios/factor-score.git
cd factor-score
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

2. Install the package in editable mode with dev dependencies:

```bash
pip install -e '.[dev]'
```

This installs `pytest`, `pytest-cov`, and the `yfinance` provider so the full test suite can run.

### Running tests

```bash
pytest
```

To see coverage:

```bash
pytest --cov=factor_score
```

### Project layout

```
factor_score/      # library source
  engine.py        # FactorEngine — main entry point
  models.py        # FactorConfig, FactorScore dataclasses
  factors/         # individual factor implementations
  providers/       # DataProvider implementations (yfinance, …)
tests/             # pytest suite
```

### Adding a factor

1. Implement the scoring logic in `factor_score/factors/`.
2. Add a weight field to `FactorConfig` in `models.py` (default to `0.0` so existing configs stay valid).
3. Wire it into `FactorEngine.score()` in `engine.py`.
4. Add tests in `tests/`.

### Adding a data provider

Implement the two-method `DataProvider` protocol (see `factor_score/providers/`) and pass an instance to `FactorEngine(provider=...)`. No base class required — duck typing is sufficient.

## License

MIT
