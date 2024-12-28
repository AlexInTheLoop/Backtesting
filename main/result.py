from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from stats import core_metrics, tail_metrics, performance_metrics
import plotly.graph_objects as go #type: ignore
from plotly.subplots import make_subplots #type: ignore
import seaborn as sns

@dataclass
class Result:
    """
    Classe pour stocker et analyser les résultats d'un backtest
    """
    positions: pd.DataFrame
    data: pd.DataFrame
    initial_capital: float
    commission: float
    slippage: float
    
    def __post_init__(self):
        """
        Initialise les calculs de base après la création de l'instance
        """
        if not isinstance(self.positions, pd.DataFrame) or 'position' not in self.positions.columns:
            raise ValueError("positions attribute must be a DataFrame with a 'position' field")
            
        if not isinstance(self.data, pd.DataFrame) or 'close' not in self.data.columns:
            raise ValueError("data attribute must be a DataFrame with a 'close' field")
            
        if len(self.positions) != len(self.data):
            raise ValueError("positions and data attributes must share the same length")
            
        if not (-1 <= self.positions['position']).all() or not (self.positions['position'] <= 1).all():
            raise ValueError("Positions must belong to [-1,1]")
        
        self.data.index = pd.to_datetime(self.data.index)
        self.positions.index = pd.to_datetime(self.positions.index)
        
        self.returns = self.data['close'].pct_change().fillna(0)
        
        self.calculate_nav()
        
        self.N = 252
        
    def calculate_nav(self):
        """
        Calcule la série de NAV en tenant compte des positions, commissions et slippage
        """

        self.nav = pd.Series(index=self.data.index, dtype=float)
        self.nav.iloc[0] = self.initial_capital
        
        prev_position = 0
        
        for i in range(1, len(self.nav)):
            current_position = self.positions['position'].iloc[i-1]
            
            ret = self.returns.iloc[i] * prev_position
            
            if current_position != prev_position:
                transaction_cost = abs(current_position - prev_position) * (self.commission + self.slippage)
            else:
                transaction_cost = 0
                
            self.nav.iloc[i] = self.nav.iloc[i-1] * (1 + ret - transaction_cost)
            
            prev_position = current_position
        
    def get_essential_metrics(self) -> Dict[str, float]:
        """
        Retourne les métriques essentielles du backtest

        Returns
        ----------
        dict
            dictionnaire avec le nom des métriques essentielles en clé et les métriques en valeurs
        """
        nav_returns = self.nav.pct_change().fillna(0)
        
        positions_series = pd.Series(self.positions['position'].values, index=self.data.index)
        
        return {
            'Total Return (%)': (self.nav.iloc[-1] / self.initial_capital - 1) * 100,
            'Annualized Return (%)': core_metrics.annualized_return(nav_returns, self.N) * 100,
            'Volatility (%)': core_metrics.annualized_std(nav_returns, self.N) * 100,
            'Sharpe Ratio': performance_metrics.sharpe_ratio(nav_returns, 0, self.N),
            'Maximum Drawdown (%)': tail_metrics.max_drawdown(self.nav) * 100,
            'Sortino Ratio': performance_metrics.sortino_ratio(nav_returns, 0, self.N),
            'Number of Trades': core_metrics.count_trades(positions_series),
            'Winning Trades (%)': core_metrics.winning_trades_percentage(positions_series,self.returns) * 100
        }
        
    def get_all_metrics(self) -> Dict[str, float]:
        """
        Retourne toutes les métriques disponibles du backtest

        Returns
        ----------
        dict
            dictionnaire avec le nom de toutes les métriques en clé et les métriques en valeurs
        """

        nav_returns = self.nav.pct_change().fillna(0)
        
        metrics = self.get_essential_metrics()
        
        additional_metrics = {
            'CAGR (%)': core_metrics.annualized_cagr(nav_returns, self.N) * 100,
            'Skewness': tail_metrics.skewness(nav_returns),
            'Kurtosis': tail_metrics.kurtosis(nav_returns),
            'Adjusted Sharpe Ratio': performance_metrics.adjusted_sharpe_ratio(nav_returns, 0, self.N),
            'Calmar Ratio': performance_metrics.calmar_ratio(nav_returns, self.nav, self.N),
            'Pain Ratio': performance_metrics.pain_ratio(nav_returns, self.nav, self.N),
            'VaR Ratio': performance_metrics.var_ratio(nav_returns, self.N),
            'CVaR Ratio': performance_metrics.cvar_ratio(nav_returns, self.N),
            'Gain to Pain Ratio': performance_metrics.gain_to_pain_ratio(nav_returns)
        }
        
        metrics.update(additional_metrics)

        return metrics
    
    def plot(self, what: str = 'nav', backend: str = 'matplotlib'):
        """
        Visualise les résultats du backtest
        
        Parameters
        ----------
        what: str
            Nom de ce que l'on veut afficher graphiquement (nav, returns ou positions
            avec par défaut la nav)
        backend: str
            Nom du style de visualisation souhaité (matplotlib, seaborn, plotly
            avec par défaut matplotlib)
        """
        
        if backend not in ['matplotlib', 'seaborn', 'plotly']:
            raise ValueError("Backend must be one of: 'matplotlib', 'seaborn', 'plotly'")
        
        if backend == 'matplotlib':
            plt.figure(figsize=(12, 6))
            
            if what == 'nav':
                plt.plot(self.nav.index, self.nav.values, linewidth=2)
                plt.title('Net Asset Value Evolution', fontsize=12)
                plt.ylabel('NAV')
            elif what == 'returns':
                nav_returns = self.nav.pct_change().fillna(0)
                plt.hist(nav_returns, bins=50, density=True)
                plt.title('Returns Distribution', fontsize=12)
                plt.ylabel('Frequency')
            elif what == 'positions':
                plt.plot(self.positions.index, self.positions['position'])
                plt.title('Position Evolution', fontsize=12)
                plt.ylabel('Position (-1 to 1)')
            plt.grid(True, alpha=0.3)
            plt.show()
            
        elif backend == 'seaborn':
            plt.figure(figsize=(12, 6))
            
            if what == 'nav':
                sns.lineplot(data=self.nav)
                plt.title('Net Asset Value Evolution', fontsize=12)
                plt.ylabel('NAV')
            elif what == 'returns':
                nav_returns = self.nav.pct_change().fillna(0)
                sns.histplot(data=nav_returns, bins=50, stat='density')
                plt.title('Returns Distribution', fontsize=12)
                plt.ylabel('Frequency')
            elif what == 'positions':
                sns.lineplot(data=self.positions['position'])
                plt.title('Position Evolution', fontsize=12)
                plt.ylabel('Position (-1 to 1)')
            sns.despine()
            plt.show()
            
        elif backend == 'plotly':            
            fig = make_subplots(rows=1, cols=1)
            
            if what == 'nav':
                fig.add_trace(go.Scatter(
                    x=self.nav.index,
                    y=self.nav.values,
                    mode='lines',
                    name='NAV',
                    line=dict(width=2)
                ))
                fig.update_layout(
                    title='Net Asset Value Evolution',
                    xaxis_title='Time',
                    yaxis_title='NAV',
                    template='ggplot2'
                )
            elif what == 'returns':
                nav_returns = self.nav.pct_change().fillna(0)
                fig.add_trace(go.Histogram(
                    x=nav_returns,
                    nbinsx=50,
                    name='Returns',
                    histnorm='probability density'
                ))
                fig.update_layout(
                    title='Returns Distribution',
                    xaxis_title='Returns',
                    yaxis_title='Density',
                    template='ggplot2'
                )
            elif what == 'positions':
                fig.add_trace(go.Scatter(
                    x=self.positions.index,
                    y=self.positions['position'],
                    mode='lines',
                    name='Position',
                    line=dict(width=2)
                ))
                fig.update_layout(
                    title='Position Evolution',
                    xaxis_title='Time',
                    yaxis_title='Position (-1 to 1)',
                    template='ggplot2'
                )
            fig.show()

    
    @staticmethod
    def compare_results(*results: 'Result', metrics: List[str] = None) -> pd.DataFrame:
        """
        Compare les résultats de plusieurs backtests
        
        Parameters
        ----------
        *results: Result
            instance de la classe Result pour faire des comparaison
        metrics: List[str] 
            Liste des métriques à comparer (si None, utilise les métriques essentielles)

        Returns
        ----------
        DataFrame
            métriques des différentes stratégies
        """
        if not results:
            raise ValueError("At least one Result object must be provided")
            
        if metrics is None:
            all_metrics = results[0].get_essential_metrics()
            metrics = list(all_metrics.keys())
        
        comparison = {}
        for i, result in enumerate(results, 1):
            all_metrics = result.get_all_metrics()
            comparison[f'Strategy {i}'] = {metric: all_metrics[metric] for metric in metrics}
            
        return pd.DataFrame(comparison)