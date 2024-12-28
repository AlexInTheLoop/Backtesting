import pytest #type: ignore
import pandas as pd
import numpy as np
from strategies.strategy_constructor import Strategy, strategy
from strategies.moving_average import ma_crossover

@pytest.fixture
def price_data():
    """Creates price data for tests"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    prices = np.sin(np.linspace(0, 4*np.pi, 100)) * 10 + 100
    return pd.DataFrame({'close': prices}, index=dates)

def test_strategy_decorator():
    """strategy decorator test"""
    @strategy(name="TestStrategy")
    def test_strategy(historical_data: pd.DataFrame, current_position: float) -> float:
        return 1.0 if historical_data['close'].iloc[-1] > 100 else -1.0
    
    assert test_strategy.__name__ == "TestStrategy"
    strategy_instance = test_strategy()
    assert isinstance(strategy_instance, Strategy)

def test_moving_average_crossover(price_data):
    """MA Crossover strategy test"""
    strategy = ma_crossover(short_window=20, long_window=50)
    
    position = strategy.get_position(price_data.iloc[:10], 0)
    assert position == 0.0
    
    position = strategy.get_position(price_data, 0)
    assert isinstance(position, float)
    assert -1.0 <= position <= 1.0

def test_strategy_position_bounds(price_data):
    """Test if positions are all in [-1,1]"""
    strategy = ma_crossover()
    position = strategy.get_position(price_data, 0)
    assert -1.0 <= position <= 1.0

class TestStrategy(Strategy):
    """Child strategy for test"""
    def get_position(self, historical_data: pd.DataFrame, current_position: float) -> float:
        return 1.0 if historical_data['close'].iloc[-1] > historical_data['close'].mean() else -1.0

def test_custom_strategy(price_data):
    """Test for a child strategy"""
    strategy = TestStrategy()
    position = strategy.get_position(price_data, 0)
    assert isinstance(position, float)
    assert -1.0 <= position <= 1.0