from strategies.strategy_constructor import strategy
import pandas as pd

@strategy(name="MA Crossover")
def ma_crossover(historical_data: pd.DataFrame, current_position: float, 
                short_window: int = 20, long_window: int = 50) -> float:
    """
    Stratégie basée sur le croisement de deux moyennes mobiles.
    
    Parameters
    ----------
    historical_data: DataFrame 
        série des données historiques
    current_position: float
        position actuelle (-1.0, 0 ou 1.0)
    short_window: int
        fenêtre de la moyenne mobile courte (par défaut à 20)
    long_window: int
        fenêtre de la moyenne mobile longue (par défaut à 50)
        
    Returns
    ----------
    current_position: float
        nouvelle position (-1.0, 0.0, ou 1.0)
    """
    if len(historical_data) < long_window:
        return 0.0
        
    prices = historical_data['close']
    short_ma = prices.rolling(window=short_window).mean()
    long_ma = prices.rolling(window=long_window).mean()
    
    # MA courte > MA longue => ACHAT
    if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
        return 1.0
    # MA courte < MA longue => VENTE
    elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
        return -1.0
    
    return float(current_position)