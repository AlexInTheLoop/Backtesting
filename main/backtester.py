from dataclasses import dataclass
import pandas as pd
from strategies.strategy_constructor import Strategy
from main.result import Result

FREQ_MAP = {
    '1min': '1min',
    '5min': '5min',
    '15min': '15min',
    '30min': '30min',
    '1H': '1h',
    '4H': '4h',
    'D': 'D',
    'W': 'W-MON', 
    'M': 'M'
}

@dataclass
class Backtester:
    """
    Classe permettant de backtester des stratégies de trading
    """
    data: pd.DataFrame
    initial_capital: float = 10000.0
    commission: float = 0.001
    slippage: float = 0.0
    rebalancing_frequency: str = 'D'
    
    def __post_init__(self):
        if self.rebalancing_frequency not in FREQ_MAP:
            raise ValueError(f"Frequency not available. Available frequencies: {', '.join(FREQ_MAP.keys())}")
            
        self.data.index = pd.to_datetime(self.data.index)
        
        if len(self.data) > 1:
            self.data_frequency = pd.infer_freq(self.data.index)
            if self.data_frequency is None:
                time_diff = (self.data.index[1] - self.data.index[0]).total_seconds()
                if time_diff < 86400:  # 86400 sec = 24h
                    self.data_frequency = f"{int(time_diff/60)}min"
                else:
                    self.data_frequency = 'D'
        else:
            self.data_frequency = 'D'
            
        data_minutes = self._freq_to_minutes(self.data_frequency)

        rebal_minutes = self._freq_to_minutes(FREQ_MAP[self.rebalancing_frequency])

        if rebal_minutes < data_minutes:
            raise ValueError(f"La fréquence de rebalancement ({self.rebalancing_frequency}) ne peut pas être plus fine que la fréquence des données ({self.data_frequency})")
    
    @staticmethod
    def _freq_to_minutes(freq: str) -> int:
        """
        Conversion d'une fréquence en minutes

        Parameter
        ----------
        freq: str 
            indicatif de la fréquence des données
            
        Returns
        ----------
        int 
            nombre de minutes par période
        """
        if 'min' in freq:
            return int(freq.replace('min', ''))
        elif 'h' in freq.lower(): 
            return int(freq[0]) * 60
        elif freq == 'D':
            return 1440  # 1440 min = 24h
        elif freq.startswith('W'):
            return 10080  # 10080 min = 1 week 
        elif freq.startswith('M'):
            return 43200  # 43200 sec = 1 month
        else:
            return 0

    @staticmethod
    def _get_period_start(timestamp: pd.Timestamp, freq: str) -> pd.Timestamp:
        """
        Identification du début de la période pour un timestamp donné

        Parameters
        ----------
        timestamp: Timestamp 
            indice temporel
        freq: float 
            fréquence des données
            
        Returns
        ----------
        timestamp 
            nouvel indice temporel pour rebalancer la position
        """

        if freq == 'M':
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif freq == 'W-MON':
            return timestamp - pd.Timedelta(days=timestamp.dayofweek)
        else:
            return timestamp.floor(freq)
    
    def run(self, strategy: Strategy) -> Result:
        """
        Exécute le backtest pour une stratégie donnée.
        
        Parameter
        ----------
        strategy: Strategy 
            stratégie backtestée
            
        Returns
        ----------
        Result 
            instance de la classe Result avec :
                - Le DataFrame des positions prises
                - Le DataFrame des données de l'actif
                - Le capital initial
                - La commission appliquée
                - Le slippage appliqué
        """
        strategy.fit(self.data)
        
        rebal_freq = FREQ_MAP[self.rebalancing_frequency]
        
        if self.rebalancing_frequency != self.data_frequency:
            resampled_data = self.data.resample(rebal_freq).agg({'close': 'last','volume': 'sum'}).ffill()
            resampled_data = resampled_data.reindex(self.data.index, method='ffill')
        else:
            resampled_data = self.data.copy()
            
        positions = []
        current_position = 0.0
        last_rebalancing_time = None
        current_rebalancing_position = 0.0
        
        for timestamp in self.data.index:
            if self.rebalancing_frequency != self.data_frequency:
                period_start = self._get_period_start(timestamp, rebal_freq)
                
                if last_rebalancing_time != period_start:
                    historical_data = resampled_data.loc[:timestamp]
                    current_rebalancing_position = strategy.get_position(historical_data, current_position)
                    last_rebalancing_time = period_start
                
                positions.append(current_rebalancing_position)
                current_position = current_rebalancing_position
            else:
                historical_data = self.data.loc[:timestamp]
                new_position = strategy.get_position(historical_data, current_position)
                new_position = new_position
                positions.append(new_position)
                current_position = new_position
        
        positions_df = pd.DataFrame({'position': positions,'timestamp': self.data.index}, index=self.data.index)
        
        return Result(
            positions=positions_df,
            data=self.data,
            initial_capital=self.initial_capital,
            commission=self.commission,
            slippage=self.slippage
        )