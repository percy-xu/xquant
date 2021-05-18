from xquant.backtest.holdings import Holdings
from xquant.util.period import Period
from dateutil.relativedelta import relativedelta

def run_backtest(start_time, end_time, stock_selection, funds, rebalance_freq) -> Holdings:
    holdings = Holdings(holdings={})
    now = start_time
    while now < end_time:
        print(f'Now processing: {now}')
        portfolio = stock_selection(funds=funds, date=now)
        next_rebalance = now + relativedelta(months=rebalance_freq)
        current_period = Period(now, next_rebalance-relativedelta(days=1))
        holdings.holdings[current_period] = portfolio
        now = next_rebalance
    
    return holdings

