from xquant.backtest.holdings import Holdings
from xquant.util.period import Period
from dateutil.relativedelta import relativedelta

def run_backtest(start_time, end_time, df_price, stock_selection, init_funds, rebalance_freq) -> Holdings:
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

