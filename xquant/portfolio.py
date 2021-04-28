import pandas as pd
import numpy as np
from typing import Union
from datetime import datetime
from xquant.util import check_time


class Portfolio():

    # constructor
    def __init__(
        self, 
        stocks:dict, 
        cash:float
        ) -> None:

        self.stocks = stocks
        self.cash = cash
    
    # methods
    def get_stock_liquidation(
        self, 
        date:Union[pd.Timestamp, datetime]
        
        ) -> float:

        '''calculates the value of all stocks in a portfolio at a given time'''
        assert check_time(date)

        agg_stock_value = 0
        sell = []

        for stock, shares in self.stocks.items():
            price = self.df_prices.at[date, stock]
            stock_value = price * shares
            # was this stock suspended for trading?
            if np.isnan(self.df_prices.at[date, stock]):
                # when was this stock last traded?
                last_traded = self.df_prices[stock].last_valid_index()
                self.cash += self.df_prices.at[last_traded, stock]
                sell.append(stock)
            else:
                agg_stock_value += stock_value

        for stock in sell:
            del self.stocks[stock]

        return agg_stock_value

    def get_net_liquidation(self, date=None):
        net_liquidation = self.get_stock_liquidation(date) + self.cash
        return net_liquidation

    def print_portfolio(self):
        for stock, shares in self.stocks.items():
            print(stock, shares)



if __name__ == '__main__':
    # p = Portfolio(stocks=1000, cash=10000)
    # print(p.stocks)
    # print(p.cash)
    pass