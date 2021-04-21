import pandas as pd
import numpy as np

def get_daily_change(prices) -> pd.Series:
    '''calculates the daily change of a prices time-series '''
    assert isinstance(prices, pd.Series), 'prices must be a pandas Series'
    assert isinstance(prices.index, pd.DatetimeIndex), 'index of prices must be a pandas.DatetimeIndex'

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
    prices = prices.loc[start_date:end_date]
    start_date, end_date = prices.index[0], prices.index[-1]
    cost = prices[start_date]
    revenue = prices[end_date]
    cum_rtn = (revenue-cost) / cost

    cum_rtn = round(cum_rtn, 4)
    return cum_rtn

def get_annualized_return(self, time_series, start_date, end_date, period='d'):
    time_series = time_series.loc[start_date:end_date]
    start_date, end_date = time_series.index[0], time_series.index[-1]
    # first get cumulative return
    cum_rtn = self.get_cumulative_return(time_series, start_date, end_date)
    # how many times should return be compounded in this period?
    if period == 'd':
        days = len(time_series.index)
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

def get_annualized_excess_return(self, strategy, benchmark, start_date, end_date):
    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    market_return = self.get_annualized_return(
        benchmark, start_date, end_date)
    strategy_return = self.get_annualized_return(
        strategy, start_date, end_date)

    ann_ex_rtn = strategy_return - market_return

    return ann_ex_rtn

def get_max_drawdown(self, time_series, start_date, end_date):
    time_series = time_series.loc[start_date:end_date]
    start_date, end_date = time_series.index[0], time_series.index[-1]
    max_drawdown = 0
    # for each day, get the lowest price in the period after
    for day in time_series.index:
        day_price = time_series[day]
        lowest = time_series.loc[day:].min()
        drawdown = (day_price-lowest) / day_price
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    max_drawdown = round(max_drawdown, 4)
    return max_drawdown

def get_strategy_volatility(self, time_series, start_date, end_date):
    time_series = time_series.loc[start_date:end_date]
    start_date, end_date = time_series.index[0], time_series.index[-1]
    time_series_chg = pd.Series(data=self.get_daily_return(
        time_series), index=time_series.index)

    strat_vo = np.std(time_series_chg) * np.sqrt(250)
    return strat_vo

def get_sharpe_ratio(self, time_series, start_date, end_date, risk_free=0.04):
    time_series = time_series.loc[start_date:end_date]
    start_date, end_date = time_series.index[0], time_series.index[-1]

    ann_rtn = self.get_annualized_return(time_series, start_date, end_date)
    excess_rtn = ann_rtn - risk_free
    vo = self.get_strategy_volatility(time_series, start_date, end_date)

    sharpe_ratio = excess_rtn / vo
    return sharpe_ratio

def get_information_ratio(self, strategy, benchmark, start_date, end_date):
    excess_return = self.get_annualized_excess_return(
        strategy, benchmark, start_date, end_date)

    daily_excess_return = self.get_daily_return(
        strategy) - self.get_daily_return(benchmark)
    daily_stdev = np.std(daily_excess_return) * np.sqrt(250)

    ir = excess_return / daily_stdev
    return ir

def get_beta(self, strategy, benchmark, start_date, end_date):
    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = self.get_daily_return(strategy)
    r_benchmark = self.get_daily_return(benchmark)

    var = np.var(r_benchmark, ddof=1)
    cov = np.cov(r_strategy, r_benchmark)[0][1]

    beta = cov/var
    return beta

def get_alpha(self, strategy, benchmark, start_date, end_date, risk_free=0.04):
    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    market_return = self.get_annualized_return(
        benchmark, start_date, end_date)
    beta = self.get_beta(strategy, benchmark, start_date, end_date)

    capm = risk_free + beta*(market_return-risk_free)
    annualized_return = self.get_annualized_return(
        strategy, start_date, end_date)

    alpha = annualized_return - capm
    return alpha

def get_win_rate(self, start_date, end_date):
    start_date, end_date = pd.to_datetime(
        start_date), pd.to_datetime(end_date)
    # trim log to fit within the time period
    log = [transaction for transaction in self.log if start_date <=
            transaction[0] <= end_date]
    # how many transactions has taken place?
    transactions = len(log) - 1
    # the initial value is the portfolio's net liquidation at day zero
    current_val = log[0][1].get_net_liquidation(log[0][0])
    # iterate over log and determine portfolio value at each transaction
    gain = 0
    for i in range(1, len(log)):
        current_date = log[i][0]
        portfolio_val = log[i][1].get_net_liquidation(current_date)
        if portfolio_val >= current_val:
            gain += 1
        current_val = portfolio_val
    # calculate win rate
    win_rate = gain / transactions
    return win_rate

def get_daily_win_rate(self, strategy, benchmark, start_date, end_date):
    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = self.get_daily_return(strategy)
    r_benchmark = self.get_daily_return(benchmark)

    daily_diff = r_strategy - r_benchmark
    win = 0
    for day in daily_diff:
        if day > 0:
            win += 1

    daily_win_rate = win / len(daily_diff)
    return daily_win_rate

def get_pl_ratio(self, start_date, end_date):
    start_date, end_date = pd.to_datetime(
        start_date), pd.to_datetime(end_date)
    # trim log to fit within the time period
    log = [transaction for transaction in self.log if start_date <=
            transaction[0] <= end_date]
    # the initial value is the portfolio's net liquidation at day zero
    current_val = log[0][1].get_net_liquidation(log[0][0])
    # iterate over log and determine portfolio value at each transaction
    profit, loss = [], []
    for i in range(1, len(log)):
        current_date = log[i][0]
        portfolio_val = log[i][1].get_net_liquidation(current_date)
        if portfolio_val >= current_val:
            profit.append(portfolio_val-current_val)
        else:
            loss.append(current_val-portfolio_val)
    # calculate average profits and losses
    avg_profit = np.mean(profit)
    avg_loss = np.mean(loss)
    # calculate P/L ratio
    pl_ratio = avg_profit / avg_loss
    return pl_ratio

def get_excess_return(self, strategy, benchmark, start_date, end_date):
    strategy = strategy.loc[start_date:end_date]
    benchmark = benchmark.loc[start_date:end_date]
    start_date, end_date = strategy.index[0], strategy.index[-1]

    r_strategy = self.get_daily_return(strategy)
    r_benchmark = self.get_daily_return(benchmark)

    excess_return = (r_strategy - r_benchmark).cumsum()
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

def get_tracking_error(self, strategy, benchmark, start_date, end_date):
    ann_ex_r = self.get_annualized_excess_return(
        strategy, benchmark, start_date, end_date)
    ir = self.get_information_ratio(
        strategy, benchmark, start_date, end_date)

    tracking_error = ann_ex_r / ir
    return tracking_error