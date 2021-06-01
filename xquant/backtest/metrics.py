from xquant.backtest.holdings import Holdings
import pandas as pd
import numpy as np
from xquant.util import check_prices, check_time
from xquant.portfolio import Portfolio
import plotly.graph_objects as go
from collections import Counter

def get_daily_returns(prices) -> pd.Series:
    '''calculates the daily returns of a prices time-series'''
    assert check_prices(prices=prices)
    prices.sort_index(inplace=True) # make sure dates is in ascending order
    daily_change = [0]
    for i in range(1, len(prices)):
        yesterday = prices[i-1]
        today = prices[i]
        change = round((today-yesterday)/yesterday, 4)
        daily_change.append(change)

    daily_change = pd.Series(data=daily_change, index=prices.index)
    return daily_change

def get_cumulative_return(prices, start_date, end_date) -> float:
    '''calculates the cumulative return between two dates'''
    assert check_prices(prices=prices)
    assert check_time(start_date=start_date, end_date=end_date)

    prices.sort_index(inplace=True) # make sure dates is in ascending order
    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]
    cost = prices[start_date]
    revenue = prices[end_date]
    cum_rtn = (revenue-cost) / cost

    cum_rtn = round(cum_rtn, 4)
    return cum_rtn

def get_annualized_return(prices, start_date, end_date, period='d') -> float:
    '''calculates the annualized return between two dates'''
    assert period in ['d','w','m'], "period must be one of 'd', 'w' or 'm'" 

    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]
    # first get cumulative return
    cum_rtn = get_cumulative_return(prices, start_date, end_date)
    # how many times should return be compounded in this period?
    if period == 'd':
        days = (end_date - start_date).days
        exp = 250/days
    elif period == 'w':
        weeks = (end_date.to_period('W') - start_date.to_period('W')).n
        exp = 52/weeks
    elif period == 'm':
        months = (end_date.to_period('M') - start_date.to_period('M')).n
        exp = 12/months
    # calculate annualized return
    ann_rtn = pow((1+cum_rtn), exp) - 1

    ann_rtn = round(ann_rtn, 4)
    return ann_rtn

def get_annualized_excess_return(strategy, benchmark, start_date, end_date) -> float:
    '''calculate the annuliazed return of a strategy compared to a benchmark'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]
    
    strategy_return = get_annualized_return(strategy, start_date, end_date)
    market_return = get_annualized_return(benchmark, start_date, end_date)

    ann_ex_rtn = strategy_return - market_return
    ann_ex_rtn = round(ann_ex_rtn, 4)
    return ann_ex_rtn

def get_max_drawdown(prices, start_date, end_date) -> float:
    '''calculates the maximum drawdown of a prices time-series between two dates'''
    assert check_prices(prices=prices)
    assert check_time(start_date=start_date, end_date=end_date)

    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]
    max_drawdown = 0
    # for each day, get the lowest price in the period after
    for day in prices.index:
        day_price = prices[day]
        lowest = prices.loc[day:].min()
        drawdown = (day_price-lowest) / day_price
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    max_drawdown = round(max_drawdown, 4)
    return max_drawdown

def get_strategy_volatility(prices, start_date, end_date) -> float:
    '''calculates the volatility of a prices time-series between two dates'''
    assert check_prices(prices=prices)
    assert check_time(start_date=start_date, end_date=end_date)

    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]
    prices_chg = pd.Series(data=get_daily_returns(prices), index=prices.index)

    strat_vo = np.std(prices_chg) * np.sqrt(250)
    strat_vo = round(strat_vo, 4)
    return strat_vo

def get_sharpe_ratio(prices, start_date, end_date, risk_free=0.04) -> float:
    '''calculates the sharpe ratio of a prices time-series between two dates'''
    assert check_prices(prices=prices)
    assert check_time(start_date=start_date, end_date=end_date)
    assert 0<=risk_free<=1, 'the risk free rate must be between 0 and 1'

    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]

    ann_rtn = get_annualized_return(prices, start_date, end_date)
    excess_rtn = ann_rtn - risk_free
    vo = get_strategy_volatility(prices, start_date, end_date)

    sharpe_ratio = excess_rtn / vo
    sharpe_ratio = round(sharpe_ratio, 4)
    return sharpe_ratio

def get_risk_adjusted_return(prices, start_date, end_date) -> float:
    '''calculates the risk-adjusted return of a prices time-series between two dates'''
    assert check_prices(prices=prices)
    assert check_time(start_date=start_date, end_date=end_date)

    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]

    ann_rtn = get_annualized_return(prices, start_date, end_date)
    vo = get_strategy_volatility(prices, start_date, end_date)

    risk_adj_rtn = ann_rtn / vo
    risk_adj_rt = round(risk_adj_rtn, 4)
    return risk_adj_rt

def get_information_ratio(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the information ratio of a prices time-series between two dates'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    excess_return = get_annualized_excess_return(strategy, benchmark, start_date, end_date)

    daily_excess_return = get_daily_returns(strategy) - get_daily_returns(benchmark)
    daily_stdev = np.std(daily_excess_return) * np.sqrt(250)

    ir = excess_return / daily_stdev
    ir = round(ir, 4)
    return ir

def get_beta(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the beta of a prices time-series between two dates'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = get_daily_returns(strategy)
    r_benchmark = get_daily_returns(benchmark)

    var = np.var(r_benchmark, ddof=1)
    cov = np.cov(r_strategy, r_benchmark)[0][1]

    beta = cov/var
    beta = round(beta, 4)
    return beta

def get_alpha(strategy, benchmark, start_date, end_date, risk_free=0.04) -> float:
    '''calculates the alpha of a prices time-series between two dates'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)
    assert 0<=risk_free<=1, 'the risk free rate must be between 0 and 1'

    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    market_return = get_annualized_return(benchmark, start_date, end_date)
    beta = get_beta(strategy, benchmark, start_date, end_date)

    capm = risk_free + beta*(market_return-risk_free) # asset price under the CAPM model
    annualized_return = get_annualized_return(strategy, start_date, end_date)

    alpha = annualized_return - capm
    alpha = round(alpha, 4)
    return alpha

def get_win_rate(start_date, end_date, holdings, df_price) -> float:
    assert check_time(start_date=start_date, end_date=end_date)
    
    periods = list(holdings.holdings.keys())
    # trim log to fit within the time period
    periods = [date for date in periods if start_date <= date.start_time <= end_date][1:]
    # how many periods are there?
    n_periods = len(periods)
    winning_periods = 0

    for period in periods:
        portfolio = holdings.holdings[period]
        # get portfolio value at start and end time
        start_val = portfolio.get_net_liquidation(period.start_time, df_price)
        end_val = portfolio.get_net_liquidation(period.end_time, df_price)
        
        # if the rebalance made a profit, increase gains by 1
        if end_val > start_val:
            winning_periods += 1

    # calculate win rate
    win_rate = winning_periods / n_periods
    return win_rate

def get_daily_win_rate(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the daily win rate of a strategy compared to a benchmark'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = get_daily_returns(strategy)
    r_benchmark = get_daily_returns(benchmark)

    daily_diff = r_strategy - r_benchmark
    win = 0
    for day in daily_diff:
        if day > 0:
            win += 1

    daily_win_rate = win / len(daily_diff)
    daily_win_rate = round(daily_win_rate, 4)
    return daily_win_rate

def get_pl_ratio(start_date, end_date, holdings, df_price):
    assert check_time(start_date=start_date, end_date=end_date)
    
    periods = list(holdings.holdings.keys())
    # trim log to fit within the time period
    periods = [date for date in periods if start_date <= date.start_time <= end_date][1:]
    profit, loss = [], []

    for period in periods:
        portfolio = holdings.holdings[period]
        # get portfolio value at start and end time
        start_val = portfolio.get_net_liquidation(period.start_time, df_price)
        end_val = portfolio.get_net_liquidation(period.end_time, df_price)
        
        # if the rebalance made a profit, increase gains by 1
        if end_val > start_val:
            profit.append(end_val - start_val)
        elif end_val < start_val:
            loss.append(start_val - end_val)
    
    # calculate average profits and losses
    avg_profit = np.mean(profit)
    avg_loss = np.mean(loss)
    # calculate P/L ratio
    pl_ratio = avg_profit / avg_loss
    return pl_ratio

def get_excess_return(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the excess return of a strategy over a benchmark between two dates'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = get_daily_returns(strategy)
    r_benchmark = get_daily_returns(benchmark)

    excess_return = (r_strategy - r_benchmark).cumsum()
    excess_return = round(excess_return, 4)
    return excess_return

def get_turnover_ratio(start_date, end_date, holdings, df_price):
    '''
    Calculates the turnover ratio of a portfolio over a holding period.
    Only long positions are taken into consideration, short positions are ignored.
    '''
    assert check_time(start_date=start_date, end_date=end_date)
    
    periods = sorted(list(holdings.holdings.keys()))
    # trim log to fit within the time period
    periods = [period for period in periods if start_date <= period.start_time <= end_date]
    rebalance_dates = [period.end_time for period in periods][:-1]
    
    start_portfolio = holdings.holdings[periods[0]]
    end_portfolio = holdings.holdings[periods[-1]]
    start_val = start_portfolio.get_net_liquidation(periods[0].start_time, df_price)
    end_val = end_portfolio.get_net_liquidation(periods[-1].end_time, df_price)

    agg_turnover = 0
    buy_value = sell_value = []

    for day in rebalance_dates:
        
        pre_portfolio = holdings.get_portfolio(day).long
        post_portfolio = holdings.get_portfolio(day + pd.Timedelta(days=1)).long
        buy_portfolio = Portfolio(long = dict(Counter(post_portfolio)-Counter(pre_portfolio)))
        sell_portfolio = Portfolio(long = dict(Counter(pre_portfolio)-Counter(post_portfolio)))

        buy_value = buy_portfolio.get_net_liquidation(day, df_price)
        sell_value = sell_portfolio.get_net_liquidation(day, df_price)

        turnover = (buy_value + sell_value) / 2
        agg_turnover += turnover

    avg_liquidation = (end_val + start_val) / 2
    n_years = periods[-1].end_time.year - periods[0].start_time.year
    avg_annual_turnover = agg_turnover / n_years
    avg_turnover_ratio = avg_annual_turnover / avg_liquidation

    return avg_turnover_ratio

def get_tracking_error(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the tracking error of a strategy compared to a benchmark'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    ann_ex_r = get_annualized_excess_return(strategy, benchmark, start_date, end_date)
    ir = get_information_ratio(strategy, benchmark, start_date, end_date)

    tracking_error = ann_ex_r / ir
    return tracking_error

def plot_performance(strategy, benchmark):

    date_range = pd.date_range(start=strategy.index[0], end=strategy.index[-1])
    benchmark = benchmark.reindex(date_range, method='ffill')

    excess_return = get_excess_return(
        strategy, benchmark, date_range[0], date_range[-1])

    # plot graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_range,
                                y=benchmark, mode='lines', name='Benchmark'))
    fig.add_trace(go.Scatter(x=date_range,
                                y=strategy, mode='lines', name='Strategy'))
    fig.add_trace(go.Scatter(x=date_range, y=excess_return *
                                100, line={'dash': 'dot'}, name='Excess Return'))
    fig.show()

def show_metrics(strategy, benchmark, holdings, df_price):
    '''
    prints out a chart that shows columns of metrics

    Parameters
    ----------
    strategy : pandas.Series
        the performance of the strategy being backtested
    benchmark : pandas.Series
        the performance of the benchmark used in backtest
    '''
    assert check_prices(strategy=strategy, benchmark=benchmark)

    start_date = strategy.index[0]
    end_date = strategy.index[-1]

    benchmark = benchmark.loc[start_date:end_date]

    date_range = pd.date_range(start=start_date, end=end_date)
    benchmark = benchmark.reindex(date_range, method='ffill')
    benchmark.fillna(method='bfill', inplace=True)

    cum_r = get_cumulative_return(strategy, start_date, end_date)
    ann_r = get_annualized_return(strategy, start_date, end_date)
    ann_ex_r = get_annualized_excess_return(
        strategy, benchmark, start_date, end_date)
    
    max_dd = get_max_drawdown(strategy, start_date, end_date)
    vo = get_strategy_volatility(strategy, start_date, end_date)
    risk_adj = get_risk_adjusted_return(strategy, start_date, end_date)
    sharpe = get_sharpe_ratio(strategy, start_date, end_date)
    ir = get_information_ratio(
        strategy, benchmark, start_date, end_date)
    beta = get_beta(strategy, benchmark, start_date, end_date)
    alpha = get_alpha(strategy, benchmark, start_date, end_date)
    win_r = get_win_rate(start_date, end_date, holdings, df_price)
    win_r_d = get_daily_win_rate(strategy, benchmark, start_date, end_date)
    pl = get_pl_ratio(start_date, end_date, holdings, df_price)
    to_r = get_turnover_ratio(start_date, end_date, holdings, df_price)
    trk_err = get_tracking_error(
        strategy, benchmark, start_date, end_date)

    print('\n============================================')
    print('| Key Metrics ')
    print('============================================')
    print(f'| Start Date:        {start_date.date()}')
    print(f'| End Date:          {end_date.date()}')
    print('============================================')
    print(f'| Cumulative Return: {round(cum_r*100, 2)}%')
    print(f'| Annualized Return: {round(ann_r*100, 2)}%')
    print(f'| Annualized Excess: {round(ann_ex_r*100, 2)}%')
    print(f'| Maximum Drawdown:  {round(max_dd*100, 2)}%')
    print('============================================')
    print(f'| Risk Adjusted:     {round(risk_adj, 3)}')
    print(f'| Information Ratio: {round(ir, 3)}')
    print(f'| Sharpe Ratio:      {round(sharpe, 3)}')
    print(f'| Volatility:        {round(vo, 3)}')
    print('============================================')
    print(f'| Alpha:             {round(alpha, 3)}')
    print(f'| Beta:              {round(beta, 3)}')
    print('============================================')
    print(f'| Win Rate:          {round(win_r*100, 2)}%')
    print(f'| Daily Win Rate:    {round(win_r_d*100, 2)}%')
    print(f'| Profit-Loss Ratio: {round(pl, 1)} : 1')
    print('============================================')
    print(f'| Turnover Ratio:    {round(to_r*100, 2)}%')
    print(f'| Tracking Error:    {round(trk_err*100, 2)}%')
    print('============================================')