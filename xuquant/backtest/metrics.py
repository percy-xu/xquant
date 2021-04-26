import pandas as pd
import numpy as np
from typing import Union
from xuquant.util import check_prices, check_time

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
        days = len(prices.index)
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

# def get_win_rate(self, start_date, end_date) -> float:
#     start_date, end_date = pd.to_datetime(
#         start_date), pd.to_datetime(end_date)
#     # trim log to fit within the time period
#     log = [transaction for transaction in self.log if start_date <=
#             transaction[0] <= end_date]
#     # how many transactions has taken place?
#     transactions = len(log) - 1
#     # the initial value is the portfolio's net liquidation at day zero
#     current_val = log[0][1].get_net_liquidation(log[0][0])
#     # iterate over log and determine portfolio value at each transaction
#     gain = 0
#     for i in range(1, len(log)):
#         current_date = log[i][0]
#         portfolio_val = log[i][1].get_net_liquidation(current_date)
#         if portfolio_val >= current_val:
#             gain += 1
#         current_val = portfolio_val
#     # calculate win rate
#     win_rate = gain / transactions
#     return win_rate

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

# def get_pl_ratio(self, start_date, end_date):
#     start_date, end_date = pd.to_datetime(
#         start_date), pd.to_datetime(end_date)
#     # trim log to fit within the time period
#     log = [transaction for transaction in self.log if start_date <=
#             transaction[0] <= end_date]
#     # the initial value is the portfolio's net liquidation at day zero
#     current_val = log[0][1].get_net_liquidation(log[0][0])
#     # iterate over log and determine portfolio value at each transaction
#     profit, loss = [], []
#     for i in range(1, len(log)):
#         current_date = log[i][0]
#         portfolio_val = log[i][1].get_net_liquidation(current_date)
#         if portfolio_val >= current_val:
#             profit.append(portfolio_val-current_val)
#         else:
#             loss.append(current_val-portfolio_val)
#     # calculate average profits and losses
#     avg_profit = np.mean(profit)
#     avg_loss = np.mean(loss)
#     # calculate P/L ratio
#     pl_ratio = avg_profit / avg_loss
#     return pl_ratio

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

# def get_turnover_ratio(self, start_date, end_date, df_prices):
#     start_date, end_date = pd.to_datetime(
#         start_date), pd.to_datetime(end_date)
#     # trim log to fit within the time period
#     log = [transaction for transaction in self.log if start_date <=
#             transaction[0] <= end_date]

#     begin_liquidation = log[0][1].get_net_liquidation(log[0][0])
#     end_liquidation = log[-1][1].get_net_liquidation(log[-1][0])
#     avg_liquidation = (end_liquidation + begin_liquidation) / 2
#     n_years = log[-1][0].year - log[0][0].year

#     history = self.get_transaction_history()
#     agg_turnover = 0
#     for i in range(1, len(history)):
#         date = log[i][0]
#         curr_transaction = history[i][date]

#         buy_portfolio = Portfolio(
#             stocks=curr_transaction['buy'], df_prices=df_prices)
#         sell_portfolio = Portfolio(
#             stocks=curr_transaction['sell'], df_prices=df_prices)

#         buy_value = buy_portfolio.get_net_liquidation(date)
#         sell_value = sell_portfolio.get_net_liquidation(date)

#         turnover = (buy_value + sell_value) / 2
#         agg_turnover += turnover

#     avg_annual_turnover = agg_turnover / n_years
#     avg_turnover_ratio = avg_annual_turnover / avg_liquidation

#     return avg_turnover_ratio

def get_tracking_error(strategy, benchmark, start_date, end_date) -> float:
    '''calculates the tracking error of a strategy compared to a benchmark'''
    assert check_prices(strategy=strategy, benchmark=benchmark)
    assert check_time(start_date=start_date, end_date=end_date)

    ann_ex_r = get_annualized_excess_return(strategy, benchmark, start_date, end_date)
    ir = get_information_ratio(strategy, benchmark, start_date, end_date)

    tracking_error = ann_ex_r / ir
    return tracking_error