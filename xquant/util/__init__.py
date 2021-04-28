import pandas as pd
import datetime

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
        if (not isinstance(value, pd.Timestamp)) or (not isinstance(value, datetime.datetime)):
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

