from abc import ABC, abstractmethod
from xquant.portfolio import Portfolio

class Strategy(ABC):
    '''
    Strategy
    --------
    An abstract base class serves as the parent class of the user's strategy. 
    The user must create a child class and implement the stock_selection method.
    '''

    def __init__(self, strategy_name) -> None:
        self.strategy_name = strategy_name

    @abstractmethod
    def stock_selection(self, funds, date) -> Portfolio:
        '''selects a portfolio of stocks and shares from the stock selection universe'''
        pass