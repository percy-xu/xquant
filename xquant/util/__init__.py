import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union

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
        if (not isinstance(value, pd.Timestamp)) and (not isinstance(value, datetime)):
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

def closest_trading_day(date, df_index, method:str=None) -> pd.Timestamp:
    '''gets the closest trading day according to a provided index'''
    assert check_time(date=date)
    assert isinstance(df_index, pd.DatetimeIndex), 'df_index must be a pandas.DatetimeIndex'
    assert method in [None, 'ffill','bfill'], "method must be one of None, 'ffill', or 'bfill'"

    date = pd.to_datetime(date)
    open_days = df_index
    try:
        idx = open_days.get_loc(date)
    except KeyError:
        idx = open_days.get_loc(date, method=method)

    day = open_days[idx]    
    return day

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
        idx = open_days.get_loc(date, method='bfill')
        next_day = open_days[idx]
    
    return next_day

def last_trading_day(date, df_index) -> pd.Timestamp:
    '''gets the last trading day before a certain date according to a provided index'''
    assert check_time(date=date)
    assert isinstance(df_index, pd.DatetimeIndex), 'df_index must be a pandas.DatetimeIndex'

    date = pd.to_datetime(date)
    open_days = df_index
    try:
        idx = open_days.get_loc(date) - 1
        last_day = open_days[idx]
    except KeyError:
        idx = open_days.get_loc(date, method='ffill')
        last_day = open_days[idx]
    
    return last_day

def business_days(month, df_index) -> pd.DatetimeIndex:
    '''returns all business days in a month accroding to a provided index'''
    assert isinstance(df_index, pd.DatetimeIndex), 'df_index must be a pandas.DatetimeIndex'

    month = pd.to_datetime(month)
    return df_index[str(month.year)+'-'+str(month.month)].index

def quarter_generator(start, end) -> None:
    '''
    A generator that yields beginnings of quarters
    '''
    assert check_time(start=start, end=end)

    date = start - timedelta(1)
    end = end - pd.tseries.offsets.BQuarterBegin(startingMonth=1)
    while date < end:
        date = pd.Timestamp(date) + pd.tseries.offsets.BQuarterBegin(startingMonth=1)
        yield date

def quarter_begin(df, start, end) -> pd.DataFrame:
    '''
    Strips df to keep only quarter begin dates
    '''
    start_date = closest_trading_day(start, df.index, 'bfill')
    end_date = closest_trading_day(end, df.index, 'ffill')
    
    dates = [i for i in quarter_generator(start, end)]
    dates = [closest_trading_day(date, df.index, 'bfill') for date in dates]
    
    return df.loc[dates]

def quarter_sum(ticker:str, quarter:tuple, df:pd.DataFrame, sum_col:str, ticker_col:Optional[str]='ticker', date_col:Optional[str]='date') -> float:
    '''
    calculates the sum of a stock's financial metrics (e.g. dividend, earnings, etc.) in a quarter
    
    Parameters
    ----------
    ticker : str
        the ticker symbol to be looked up
    quarter: tuple
        the quarter to be looked up, e.g. 2nd quarter of 2021 is (2021, 2)
    df : pd.DataFrame
        the DataFrame where data is stored
    sum_col : str
        name of the column that contains the financial metric data to be summed
    ticker_col : str, optional (default = 'ticker')
        name of the column that contains the stock ticker symbols
    date_col : str, optional (default = 'date')
        name of the column that contains dates
    '''
    year = quarter[0]
    quarter = quarter[1]

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

def get_index_weights(df_mktcap:pd.DataFrame, df_components:pd.DataFrame, date:Union[pd.Timestamp, datetime]) -> pd.Series:
    '''
    calculates the weight for member stocks in a cap-weighted index at a certain date

    Parameters
    ----------
    df_mktcap : pandas.DataFrame
        DataFrame that has DatetimeIndex and tickers as columns
    df_components : pandas.DataFrame
        DataFrame that has includ and exclude columns of stocks in index
    date: pandas.Timestamp or datetime.datetime

    Example
    -------
    >>> df_mktcap
                 A   B   C
    date
    2005-01-01  70  20  10
    2010-01-01  75  15  10
    2015-01-01  60  20  20
    2020-01-01  50  20  30
    
    >>> df_components
    ticker    included    excluded
    A       2000-01-01         NaT
    B       2000-01-01  2012-01-01
    C       2010-01-01         NaT

    >>> get_index_weights(df_mktcap, df_components, pd.Timestamp('2010-01-01'))
        weight
    A     0.75
    B     0.15
    C     0.10

    >>> get_index_weights(df_mktcap, df_components, pd.Timestamp('2015-01-01'))
        weight
    A     0.75
    C     0.25
    '''
    assert check_time(date=date)

    # only need market cap data at date
    mktcap = df_mktcap.loc[closest_trading_day(date, df_mktcap.index, 'bfill')]
    # get all components of index at date
    df_components = df_components[(df_components['included'] <= date) & (date < df_components['excluded'])]
    components = [stock for stock in df_components['ticker'] if stock in mktcap.index] # keep only stocks with market cap data
    mktcap = mktcap.loc[components]
    
    weight = (mktcap/mktcap.sum()).rename('weight')
    return weight

if __name__ == '__main__':
    get_index_weights()