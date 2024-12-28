import pytest #type: ignore
import pandas as pd
import numpy as np
from pathlib import Path

@pytest.fixture
def sample_data():
    """Creates a small dataset to run tests"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = {
        'close': [float(x) for x in [100, 102, 101, 103, 102, 104, 103, 105, 106, 104]],
        'volume': [1000] * 10
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def btc_data():
    """Load a dataset for tests"""
    data_path = Path("data/test_BTC_daily.csv")
    if not data_path.exists():
        pytest.skip("Le fichier de données BTC n'est pas disponible")
    return pd.read_csv(data_path, index_col=0, parse_dates=True)

def test_csv_loading(btc_data):
    """Real data importation test (with .csv)"""
    assert isinstance(btc_data, pd.DataFrame)
    assert not btc_data.empty
    assert 'close' in btc_data.columns

def test_data_format(sample_data):
    """Data format test"""
    assert isinstance(sample_data.index, pd.DatetimeIndex)
    assert 'close' in sample_data.columns
    assert sample_data['close'].dtype in [np.float64, np.float32]

def test_data_continuity(sample_data):
    """Data continuity test"""
    assert sample_data.index.is_monotonic_increasing
    assert not sample_data.index.has_duplicates
    assert not sample_data['close'].isnull().any()