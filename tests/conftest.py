from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_A = ROOT / "data" / "examples" / "TRACES_sample_52x10_dataset_A1.xlsx"
SAMPLE_B = ROOT / "data" / "examples" / "TRACES_sample_52x10_dataset_B1.xlsx"


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(12345)


@pytest.fixture
def sample_path() -> Path:
    return SAMPLE_A


@pytest.fixture
def synthetic_frame(rng: np.random.Generator) -> pd.DataFrame:
    """Series with known structure: linear, lagged (x leads by 3), independent noise."""
    n = 120
    base = rng.normal(size=n + 3)
    x = base[3:]
    return pd.DataFrame(
        {
            "time": np.arange(n),
            "x": x,
            "linear": 2.0 * x + rng.normal(scale=0.2, size=n),
            "lagged": base[:-3] + rng.normal(scale=0.2, size=n),  # lagged[t] = x[t-3]
            "noise": rng.normal(size=n),
        }
    )
