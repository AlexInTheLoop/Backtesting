from tests.test_metrics import (
    returns_data,
    positions_data,
    test_annualized_return,
    test_annualized_std,
    test_sharpe_ratio,
    test_max_drawdown,
    test_count_trades,
    test_winning_trades_percentage
)

from tests.test_strategy import (
    price_data,
    test_strategy_decorator,
    test_moving_average_crossover,
    test_strategy_position_bounds,
    test_custom_strategy
)

from tests.test_backtester import (
    daily_data,
    intraday_data,
    btc_data,
    test_backtester_initialization,
    test_backtester_with_strategy,
    test_backtester_rebalancing_daily,
    test_backtester_rebalancing_intraday,
    test_backtester_invalid_frequency,
    test_backtester_frequency_validation,
    test_backtester_with_costs,
    test_backtester_with_real_data
)

from tests.test_data_utils import (
    sample_data,
    test_csv_loading,
    test_data_format,
    test_data_continuity
)

from tests.test_result import (
    sample_result,
    multiple_results,
    test_result_initialization,
    test_essential_metrics,
    test_all_metrics,
    test_nav_calculation,
    test_plotting_functions,
    test_compare_results,
    test_error_handling
)

__all__ = [
    # Test fixtures
    'returns_data',
    'positions_data',
    'price_data',
    'daily_data',
    'intraday_data',
    'btc_data',
    'sample_data',
    'sample_result',
    'multiple_results',

    # Metric tests
    'test_annualized_return',
    'test_annualized_std',
    'test_sharpe_ratio',
    'test_max_drawdown',
    'test_count_trades',
    'test_winning_trades_percentage',

    # Strategy tests
    'test_strategy_decorator',
    'test_moving_average_crossover',
    'test_strategy_position_bounds',
    'test_custom_strategy',

    # Backtester tests
    'test_backtester_initialization',
    'test_backtester_with_strategy',
    'test_backtester_rebalancing_daily',
    'test_backtester_rebalancing_intraday',
    'test_backtester_invalid_frequency',
    'test_backtester_frequency_validation',
    'test_backtester_with_costs',
    'test_backtester_with_real_data',

    # Data utility tests
    'test_csv_loading',
    'test_data_format',
    'test_data_continuity',

    # Result tests
    'test_result_initialization',
    'test_essential_metrics',
    'test_all_metrics',
    'test_nav_calculation',
    'test_plotting_functions',
    'test_compare_results',
    'test_error_handling'
]