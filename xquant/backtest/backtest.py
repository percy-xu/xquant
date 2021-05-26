from xquant.backtest.holdings import Holdings
from xquant.util.period import Period
from dateutil.relativedelta import relativedelta

def run_backtest(start_time, end_time, df_price, stock_selection, init_funds, rebalance_freq) -> Holdings:
    '''
    Driver code that initiates the back-testing process

    Parameters
    ----------
    start_time : datetime.datetime or pandas.Timestamp
        Start time for the back-test period
    end_time : datetime.datetime or pandas.Timestamp
        End time for the back-test period
    df_price : pandas.DataFrame
        Prices dataframe with DatetimeIndex and ticker symbols as columns
    stock_selection : a function (see xquant.strategy.Strategy.stock_selection)
        A function that selects stocks for inclusion in a cross-section
    init_funds : int or float
        The attributtable funds at start_time
    rebalance_freq: int
        Rebalance frequency, in months
    '''
    holdings = Holdings(holdings={})
    now = start_time
    last_portfolio = None
    while now < end_time:
        print(f'Now processing: {now}')
        if now == start_time:
            portfolio = stock_selection(funds=init_funds, date=now)
        else:
            portfolio = stock_selection(funds=last_portfolio.get_net_liquidation(now, df_price), date=now)

        next_rebalance = now + relativedelta(months=rebalance_freq)
        current_period = Period(now, next_rebalance-relativedelta(days=1))
        holdings.holdings[current_period] = portfolio
        now = next_rebalance
        last_portfolio = portfolio
    
    return holdings