import pandas as pd
import numpy as np
from typing import Union
from datetime import datetime
from xquant.util import check_time

class Portfolio():

    def __init__(self, long:dict, short:dict, cash:float) -> None:
        self.long = long
        self.short = short
        self.cash = cash
    
    def get_stock_liquidation(
        self, 
        date:Union[pd.Timestamp, datetime],
        df_prices:pd.DataFrame
        ) -> float:

        '''calculates the value of all long/short positions in a portfolio at a given time'''
        assert check_time(date)

        df_prices = df_prices.loc[:date] # trim df to be within valid dates
        agg_stock_value = 0

        # first, consider long positions
        for stock, shares in self.long.items():
            try:
                long_price = df_prices.at[date, stock]
            except KeyError:
                # when was this stock last traded?
                last_traded = df_prices[stock].last_valid_index()
                long_price = df_prices.at[last_traded, stock]

            long_stock_value = long_price * shares
            agg_stock_value += long_stock_value

        # then, consider short positions
        for stock, shares in self.short.items():
            try:
                short_price = df_prices.at[date, stock]
            except KeyError:
                # when was this stock last traded?
                last_traded = df_prices[stock].last_valid_index()
                short_price = df_prices.at[last_traded, stock]

            short_stock_value = short_price * shares
            agg_stock_value -= short_stock_value

        return agg_stock_value

    def get_net_liquidation(self, date=None):
        net_liquidation = self.get_stock_liquidation(date) + self.cash
        return net_liquidation

    def print_portfolio(self):
        print('LONG POSITIONS')
        print('--------------')
        for stock, shares in self.long.items():
            print(stock, shares)
        
        if self.short.items() != 0:
            print('SHORT POSITIONS')
            print('---------------')
        for stock, shares in self.short.items():
            print(stock, shares)

if __name__ == '__main__':
    pass