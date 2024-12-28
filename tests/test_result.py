import pytest #type: ignore
import pandas as pd
import numpy as np
from main.result import Result

@pytest.fixture
def sample_result():
    """Fixture pour créer un objet Result de test"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'close': np.sin(np.linspace(0, 4*np.pi, 100)) * 10 + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    positions = pd.DataFrame({
        'position': np.random.choice([-1, 0, 1], size=100),
        'timestamp': dates
    })
    
    return Result(
        positions=positions,
        data=data,
        initial_capital=10000,
        commission=0.001,
        slippage=0.001
    )

@pytest.fixture
def multiple_results():
    """Creates two Result objects to perform comparisons"""
    results = []
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    for i in range(2):
        data = pd.DataFrame({
            'close': (np.sin(np.linspace(0, 4*np.pi, 100)) + i) * 10 + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        positions = pd.DataFrame({
            'position': np.random.choice([-1, 0, 1], size=100),
            'timestamp': dates
        })
        
        results.append(Result(
            positions=positions,
            data=data,
            initial_capital=10000,
            commission=0.001,
            slippage=0.001
        ))
    
    return results

def test_result_initialization(sample_result):
    """Resul object initialisation test"""
    assert isinstance(sample_result.nav, pd.Series)
    assert len(sample_result.nav) > 0
    assert hasattr(sample_result, 'returns')
    assert isinstance(sample_result.returns, pd.Series)

def test_essential_metrics(sample_result):
    """Essential metrics computation test"""
    metrics = sample_result.get_essential_metrics()
    
    expected_metrics = {
        'Total Return (%)',
        'Annualized Return (%)',
        'Volatility (%)',
        'Sharpe Ratio',
        'Maximum Drawdown (%)',
        'Sortino Ratio',
        'Number of Trades',
        'Winning Trades (%)'
    }
    assert set(metrics.keys()) == expected_metrics
    assert isinstance(metrics['Sharpe Ratio'], float)
    assert -100 <= metrics['Maximum Drawdown (%)'] <= 0
    assert isinstance(metrics['Number of Trades'], int)
    assert 0 <= metrics['Winning Trades (%)'] <= 100

def test_all_metrics(sample_result):
    """All metrics computation test"""
    metrics = sample_result.get_all_metrics()
    
    essential_metrics = set(sample_result.get_essential_metrics().keys())
    assert essential_metrics.issubset(set(metrics.keys()))
    
    additional_metrics = {
        'CAGR (%)',
        'Skewness',
        'Kurtosis',
        'Adjusted Sharpe Ratio',
        'Calmar Ratio',
        'Pain Ratio',
        'VaR Ratio',
        'CVaR Ratio',
        'Gain to Pain Ratio'
    }
    assert additional_metrics.issubset(set(metrics.keys()))

def test_nav_calculation(sample_result):
    """NAV computation test"""
    assert len(sample_result.nav) == len(sample_result.data)
    assert sample_result.nav.index.equals(sample_result.data.index)
    assert sample_result.nav.iloc[0] == sample_result.initial_capital
    assert not sample_result.nav.isnull().any()

def test_plotting_functions(sample_result):
    """Visualisation test for all data types and plot style"""
    for plot_type in ['nav', 'returns', 'drawdown', 'positions']:
        for backend in ['matplotlib', 'seaborn','plotly']:
            sample_result.plot(what=plot_type, backend=backend)
            
    with pytest.raises(ValueError):
        sample_result.plot(what='nav', backend='invalid_backend')

def test_compare_results(multiple_results):
    """Comparison test for several results"""
    comparison = Result.compare_results(*multiple_results)
    
    assert isinstance(comparison, pd.DataFrame)
    
    assert all(f'Strategy {i+1}' in comparison.columns 
              for i in range(len(multiple_results)))
    
    essential_metrics = set(multiple_results[0].get_essential_metrics().keys())
    assert essential_metrics.issubset(set(comparison.index))
    
    specific_metrics = ['Sharpe Ratio', 'Maximum Drawdown (%)', 'Total Return (%)']
    comparison_specific = Result.compare_results(*multiple_results, metrics=specific_metrics)
    assert set(comparison_specific.index) == set(specific_metrics)

def test_error_handling():
    """Error management during initialisation test"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({'close': np.random.randn(100)}, index=dates)
    positions = pd.DataFrame({'position': np.random.choice([-1, 0, 1], size=99)})  # Taille incorrecte
    
    with pytest.raises(ValueError):
        Result(
            positions=positions,
            data=data,
            initial_capital=10000,
            commission=0.001,
            slippage=0.001
        )
    
    with pytest.raises(ValueError):
        Result(
            positions=pd.DataFrame({'position': np.random.randn(100)}),  # Positions invalides
            data=data,
            initial_capital=10000,
            commission=0.001,
            slippage=0.001
        )