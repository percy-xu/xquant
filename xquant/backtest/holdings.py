from datetime import datetime
from xquant.util import check_time
from xquant.util.period import Period
from xquant.portfolio import Portfolio
from typing import Union
import pickle
from os import getcwd
from pandas import Timestamp, Series, date_range


class Holdings():
    '''
    Holdings
    --------
    A class representation of historical holdings of a strategy

    Parameters
    ----------
    holdings: a dict that has xquant.util.period.Period objects as keys and xquant.portfolio.Portfolio objects as values
    '''

    def __init__(self, holdings: dict) -> None:
        self.holdings = holdings

    def get_portfolio(self, time: Union[datetime, Timestamp]) -> Portfolio:
        '''returns the portfolio at a certain time'''
        assert check_time
        for period, portfolio in self.holdings.items():
            if period.contains_time(time):
                return portfolio
        raise Exception('date not within holdings history')

    def generate_performance(self, df_price, normalize=100) -> Series:
        start_date = sorted([key.start_time for key in self.holdings.keys()])[0]
        end_date = sorted([key.end_time for key in self.holdings.keys()])[-1]

        index = date_range(start=start_date, end=end_date)
        values = []
        for day in index:
            portfolio = self.get_portfolio(day)
            values.append(portfolio.get_net_liquidation(day, df_price))
        
        values = [value/values[0] * normalize for value in values]
        performance = Series(index=index, data=values)

        return performance
        

def export_holdings(holdings) -> None:
    with open(f'holdings_{hex(id(holdings))}.dat', "wb") as f:
        pickle.dump(holdings, f)
    print(f'[Saving...] holdings saved to {getcwd()}')


def import_holdings(path) -> Holdings:
    with open(path, 'rb') as f:
        holdings = pickle.load(f)
        f.close()
    return holdings


if __name__ == '__main__':
    pass
