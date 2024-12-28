from strategies.strategy_constructor import strategy
import pandas as pd

@strategy(name="RSI")
def rsi_strategy(historical_data: pd.DataFrame, current_position: float,
                rsi_period: int = 14, overbought: float = 70, oversold: float = 30) -> float:
    """
    Stratégie basée sur le  Relative Strength Index :
        - Achat en zone de survente
        - Vente en zone de surachat
    
    Parameters
    ----------
    historical_data: DataFrame 
        série de données historiques
    current_position: float
        position actuelle (-1.0, 0 ou 1.0)
    rsi_period: int
        période pour le calcul du RSI (par défaut à 14)
    overbought: float
        début de la zone de surachat (par défaut à 70)
    oversold: float
        début de la zone de survente (par défaut à 30)
        
    Returns
    ----------
    current_position
        nouvelle position (-1.0, 0.0, ou 1.0)
    """

    if len(historical_data) < rsi_period:
        return 0.0
    
    close_prices = historical_data['close']
    abs_return = close_prices.diff()
    
    gains = (abs_return.where(abs_return > 0, 0)).rolling(window=rsi_period).mean()
    losses = (-abs_return.where(abs_return < 0, 0)).rolling(window=rsi_period).mean()
    
    rsi = 100 - (100 / (1 + gains / losses))
    
    if rsi.iloc[-1] < oversold:
        return 1.0
    elif rsi.iloc[-1] > overbought:
        return -1.0
    
    return float(current_position)