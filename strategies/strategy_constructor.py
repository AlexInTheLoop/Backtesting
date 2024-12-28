from abc import ABC, abstractmethod
from typing import Callable
import pandas as pd
import inspect

class Strategy(ABC):
    """
    Classe abstraite utilisée pour set up l'interface pour les stratégies de trading
    """
    
    @abstractmethod
    def get_position(self, historical_data: pd.DataFrame, current_position: float) -> float:
        """
        Détermine la position à prendre en fonction des données historiques.
        
        Parameters
        ----------
        historical_data: DataFrame 
            série de données historiques
        current_position: float 
            position actuelle (-1.0, 0 ou 1.0)
            
        Returns
        ----------
        float 
            nouvelle position désirée (-1.0, 0 ou 1.0)
        """
        pass
        
    def fit(self, data: pd.DataFrame) -> None:
        """
        Méthode optionnelle pour optimiser les paramètres de la stratégie.
        
        Parameters
        ----------
        data: DataFrame 
            série de données d'entraînement
        """
        pass

def strategy(*, name: str) -> Callable:
    """
    Décorateur pour créer une stratégie simple à partir d'une fonction.
    
    Parameters
    ----------
    name: str 
        nom de la stratégie
    """
    def decorator(func: Callable[[pd.DataFrame, float], float]) -> Strategy:
        sig = inspect.signature(func)
        strategy_params = [param for param in sig.parameters.keys()][2:]
        param_defaults = {param: sig.parameters[param].default for param in strategy_params}

        class SimpleStrategy(Strategy):
            def __init__(self, **kwargs):
                for param in strategy_params:
                    setattr(self, param, kwargs.get(param, param_defaults[param]))
            
            def get_position(self, historical_data: pd.DataFrame, current_position: float) -> float:
                params = {param: getattr(self, param) for param in strategy_params}
                return func(historical_data, current_position, **params)
        
        SimpleStrategy.__name__ = name
        return SimpleStrategy
        
    return decorator