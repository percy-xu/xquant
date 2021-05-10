from datetime import datetime
from xquant.util import check_time
from xquant.util.period import Period
from xquant.portfolio import Portfolio
from typing import Union
import pickle
from os import getcwd
from pandas import Timestamp


class Holdings():
    '''
    Holdings
    --------
    A class representation of historical holdings of a strategy

    Parameters
    ----------
    holdings: a dict that has xquant Period objects as keys and xquant Portfolio objects as values
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
