import pytest #type: ignore
import pandas as pd
import numpy as np
from stats import core_metrics, performance_metrics, tail_metrics

@pytest.fixture
def returns_data():
    """Creates a returns series for tests"""
    return pd.Series([0.01, -0.02, 0.03, -0.01, 0.02], name='returns')

@pytest.fixture
def positions_data():
    """Creates a positions series for tests"""
    return pd.Series([0, 1, 1, -1, -1, 0], name='position')

def test_annualized_return(returns_data):
    """Annualized return test"""
    result = core_metrics.annualized_return(returns_data, N=252)
    assert isinstance(result, float)
    assert not np.isnan(result)

def test_annualized_std(returns_data):
    """Annualized volatility test"""
    result = core_metrics.annualized_std(returns_data, N=252)
    assert isinstance(result, float)
    assert result >= 0
    assert not np.isnan(result)

def test_sharpe_ratio(returns_data):
    """Sharpe ratio test"""
    result = performance_metrics.sharpe_ratio(returns_data, risk_free_rate=0.0, N=252)
    assert isinstance(result, float)
    assert not np.isnan(result)

def test_max_drawdown():
    """Maximum drawdown test"""
    nav = pd.Series([100, 95, 90, 95, 100, 85, 90])
    result = tail_metrics.max_drawdown(nav)
    assert isinstance(result, float)
    assert result <= 0
    assert abs(result - (-0.15)) < 1e-6

def test_count_trades(positions_data):
    """Number of trades test"""
    n_trades = core_metrics.count_trades(positions_data)
    assert isinstance(n_trades, int)
    assert n_trades == 4

def test_winning_trades_percentage():
    """WWin rate test"""
    positions = pd.Series([0, 1, 1, -1, -1, 0])
    returns = pd.Series([0.01, 0.02, -0.03, -0.02, 0.01, 0.01])
    result = core_metrics.winning_trades_percentage(positions, returns)
    assert isinstance(result, float)
    assert 0 <= result <= 1