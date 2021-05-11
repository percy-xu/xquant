import pandas as pd
import datetime
from typing import Optional

def check_prices(**kwargs) -> bool:
    '''checks if one or more series of prices are of correct types'''
    for key, value in kwargs.items():
        if not isinstance(value, pd.Series):
            print(f'{key} must be a pandas.Series')
            return False
        elif not isinstance(value.index, pd.DatetimeIndex): 
            print(f'index of {key} must be a pandas.DatetimeIndex')
            return False
    return True

def check_time(**kwargs) -> bool:
    '''checks if one or more timestamps are of correct types'''
    for key, value in kwargs.items():
        if (not isinstance(value, pd.Timestamp)) and (not isinstance(value, datetime.datetime)):
            print(f'{key} must be a pandas.Timestamp or datetime.datetime')
            return False
    return True

def convert_ticker(ticker) -> str:
    '''converts ticker symbol for easier complementary API usage'''
    assert ('XSHG' in ticker) or ('XSHE' in ticker) or ('SH' in ticker) or ('SZ' in ticker), 'Invalid ticker symbol'

    if 'XSHG' in ticker:
        ticker = ticker.replace('.XSHG', '.SH')
    elif 'XSHE' in ticker:
        ticker = ticker.replace('.XSHE', '.SZ')
    elif 'SH' in ticker:
        ticker = ticker.replace('.SH', '.XSHG')
    elif 'SZ' in ticker:
        ticker = ticker.replace('.SZ', '.XSHE')
    return ticker

def add_suffix(ticker:str) -> str:
    '''
    Adds Shanghai or Shenzhen stock exchange suffix (.SH or .SZ) to a ticker

    Parameters
    ----------
    ticker : str
        the ticker symbol to add suffix onto

    Examples
    --------
    >>> from xquant.util import add_suffix
    >>> add_suffix('1')
    '000001.SZ'
    >>> add_suffix('300001')
    '300001.SZ'
    >>> add_suffix('600001')
    '600001.SH'
    '''
    ticker = ticker.zfill(6)
    if len(ticker) > 6:
        raise Exception('Cannot interpret ticker symbol')
    
    if ticker[0] == '6':
        ticker += '.SH'
    else:
        ticker += '.SZ'
    
    return ticker

def next_trading_day(date, df_index) -> pd.Timestamp:
    '''gets the next trading day after a certain date according to a provided index'''
    assert check_time(date=date)
    assert isinstance(df_index, pd.DatetimeIndex), 'df_index must be a pandas.DatetimeIndex'

    date = pd.to_datetime(date)
    open_days = df_index
    try:
        idx = open_days.get_loc(date) + 1
        next_day = open_days[idx]
    except KeyError:
        idx = open_days.get_loc(date, method='backfill')
        next_day = open_days[idx]
    
    return next_day

def business_days(month, df_index) -> pd.DatetimeIndex:
    '''returns all business days in a month accroding to a provided index'''
    assert isinstance(df_index, pd.DatetimeIndex), 'df_index must be a pandas.DatetimeIndex'

    month = pd.to_datetime(month)
    return df_index[str(month.year)+'-'+str(month.month)].index

def quarter_sum(ticker:str, year:int, quarter:int, df:pd.DataFrame, sum_col:str, ticker_col:Optional[str]='ticker', date_col:Optional[str]='date') -> float:
    '''
    calculates the sum of a stock's financial metrics (e.g. dividend, earnings, etc.) in a quarter
    
    Parameters
    ----------
    ticker : str
        the ticker symbol to be looked up
    year : int
        the year to be looked up
    quarter: int
        the quarter to be looked up, one of 1, 2, 3 or 4
    df : pd.DataFrame
        the DataFrame where data is stored
    sum_col : str
        name of the column that contains the financial metric data to be summed
    ticker_col : str, optional (default = 'ticker')
        name of the column that contains the stock ticker symbols
    date_col : str, optional (default = 'date')
        name of the column that contains dates
    '''
    
    assert isinstance(year, int), 'year must be an int'
    assert quarter in [1,2,3,4], 'quarter must be one of 1, 2, 3, or 4'
    assert isinstance(ticker, str), 'ticker must be a str'
        
    if quarter == 1:
        start = datetime(year, 1, 1)
        end = datetime(year, 3, 31)
    elif quarter == 2:
        start = datetime(year, 4, 1)
        end = datetime(year, 6, 30)
    elif quarter == 3:
        start = datetime(year, 7, 1)
        end = datetime(year, 9, 30)
    else:
        start = datetime(year, 10, 1)
        end = datetime(year, 12, 31)
    
    df = df[df[ticker_col]==ticker] # look up ticker symbol
    df = df[(start<=df[date_col]) & (df[date_col]<=end)] # look up date range
    
    return df[sum_col].sum()

if __name__ == '__main__':
    pass