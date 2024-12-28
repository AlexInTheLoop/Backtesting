import pytest #type: ignore
import pandas as pd
import numpy as np
from main.backtester import Backtester
from strategies.moving_average import ma_crossover

@pytest.fixture
def daily_data():
    """Creates simulated daily data for tests"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    prices = np.sin(np.linspace(0, 4*np.pi, 100)) * 10 + 100
    return pd.DataFrame({'close': prices, 'volume': np.random.randint(1000, 10000, 100)}, index=dates)

@pytest.fixture
def intraday_data():
    """Creates intraday data for tests"""
    dates = pd.date_range(start='2023-01-01 09:30:00', periods=100, freq='5T')
    prices = np.sin(np.linspace(0, 4*np.pi, 100)) * 10 + 100
    return pd.DataFrame({'close': prices, 'volume': np.random.randint(1000, 10000, 100)}, index=dates)

@pytest.fixture
def btc_data():
    """Load a dataset for tests"""
    try:
        return pd.read_csv("data/test_BTC_daily.csv", index_col=0, parse_dates=True)
    except FileNotFoundError:
        pytest.skip("Le fichier de données BTC n'est pas disponible")

def test_backtester_initialization(daily_data):
    """Test backtester initiation"""
    backtester = Backtester(daily_data)
    assert backtester.data.equals(daily_data)
    assert backtester.initial_capital == 10000.0
    assert backtester.commission == 0.001
    assert backtester.slippage == 0.0
    assert backtester.rebalancing_frequency == 'D'

def test_backtester_with_strategy(daily_data):
    """Strategy execution test"""
    backtester = Backtester(daily_data)
    strategy = ma_crossover(short_window=20, long_window=50)
    result = backtester.run(strategy)
    
    assert hasattr(result, 'nav')
    assert isinstance(result.nav, pd.Series)
    assert len(result.nav) == len(daily_data)
    assert result.nav.index.equals(daily_data.index)

def test_backtester_rebalancing_daily(daily_data):
    """Test for several rebalancing frequencies with daily data"""
    frequencies = ['D', 'W', 'M']
    strategy = ma_crossover()
    
    for freq in frequencies:
        backtester = Backtester(daily_data, rebalancing_frequency=freq)
        result = backtester.run(strategy)
        assert len(result.positions) == len(daily_data)

def test_backtester_rebalancing_intraday(intraday_data):
    """Test for several rebalancing frequencies with intraday data"""
    frequencies = ['5min', '15min', '30min', '1H', '4H']
    strategy = ma_crossover()
    
    for freq in frequencies:
        backtester = Backtester(intraday_data, rebalancing_frequency=freq)
        result = backtester.run(strategy)
        assert len(result.positions) == len(intraday_data)

def test_backtester_invalid_frequency(daily_data):
    """Test if the backtester reject invalid frequencies"""
    with pytest.raises(ValueError):
        Backtester(daily_data, rebalancing_frequency='Y')

def test_backtester_frequency_validation(daily_data, intraday_data):
    """Frequency validation test according to the data frequency"""
    # Impossible to rebalance every minute with daily frequencies
    with pytest.raises(ValueError):
        Backtester(daily_data, rebalancing_frequency='1min')
    
    # Possible to rebalance every 5 minutes with data of 5-minutes frequency
    backtester = Backtester(intraday_data, rebalancing_frequency='5min')
    assert backtester.rebalancing_frequency == '5min'

def test_backtester_with_costs(daily_data):
    """Transaction cost impact test"""
    strategy = ma_crossover()
    
    # Transaction costs off
    backtester_no_costs = Backtester(daily_data, commission=0, slippage=0)
    result_no_costs = backtester_no_costs.run(strategy)
    
    # Transaction costs on
    backtester_with_costs = Backtester(daily_data, commission=0.001, slippage=0.001)
    result_with_costs = backtester_with_costs.run(strategy)
    
    # NAV with transaction costs off > NAV with transaction costs on
    assert result_with_costs.nav.iloc[-1] <= result_no_costs.nav.iloc[-1]

def test_backtester_with_real_data(btc_data):
    """Test with real data"""
    backtester = Backtester(btc_data)
    strategy = ma_crossover()
    result = backtester.run(strategy)
    
    assert not result.nav.isnull().any()
    assert len(result.nav) == len(btc_data)
    assert all(-1 <= pos <= 1 for pos in result.positions['position'])