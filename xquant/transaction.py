from datetime import datetime
import pandas as pd
from xquant.portfolio import Portfolio
from typing import Union


def buy(portfolio: Portfolio,
        df_prices: pd.DataFrame,
        ticker: str,
        shares: float,
        date: Union[pd.Timestamp, datetime]) -> Portfolio:
    # calculate total transaction value
    price = df_prices.at[date, ticker]
    total_value = price * shares
    # is there enough cash in the portfolio?
    if portfolio.cash < total_value:
        raise Exception('Insufficient cash, cannot fill order')
    # deduct from cash
    else:
        portfolio.cash -= total_value
    # add to long positions
        if ticker in portfolio.long.keys:
            portfolio.long[ticker] += shares
        else:
            portfolio.long[ticker] = shares
        return portfolio


def sell(portfolio: Portfolio,
         df_prices: pd.DataFrame,
         ticker: str,
         shares: float,
         date: Union[pd.Timestamp, datetime]) -> Portfolio:
    # is there enough shares to sell?
    if ticker not in portfolio.long.keys or portfolio.long[ticker] < shares:
        raise Exception(
            'Do not have enough long positions to fill order, please use the short method to open a short position')
    else:
        # deduct from long positions
        portfolio.long[ticker] -= shares
        # calculate total transaction value
        price = df_prices.at[date, ticker]
        total_value = price * shares
        # add to cash
        portfolio.cash += total_value
        return portfolio


def short(portfolio: Portfolio,
          df_prices: pd.DataFrame,
          ticker: str,
          shares: float,
          date: Union[pd.Timestamp, datetime]) -> Portfolio:

    # add to short positions
    if ticker in portfolio.short.keys:
        portfolio.short[ticker] += shares
    else:
        portfolio.short[ticker] = shares
    # calculate total transaction value
    price = df_prices.at[date, ticker]
    total_value = price * shares
    # add to cash
    portfolio.cash += total_value
    return portfolio
