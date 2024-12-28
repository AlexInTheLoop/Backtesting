from strategies.strategy_constructor import Strategy, strategy
from strategies.moving_average import ma_crossover as MovingAverageCrossover
from strategies.RSI import rsi_strategy as RSIStrategy
from strategies.arima import ARIMAStrategy
from strategies.linear_trend import LinearTrendStrategy

__all__ = [
            'Strategy', 
            'strategy', 
            'MovingAverageCrossover', 
            'RSIStrategy', 
            'ARIMAStrategy', 
            'LinearTrendStrategy'
            ]
