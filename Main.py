import backtrader as bt
from datetime import datetime
import pandas as pd

from clenow_momentum_strategy.ClenowMomentumStrategy import ClenowMomentumStrategy
from clenow_momentum_strategy.PortfolioObserver import PortfolioObserver
from clenow_momentum_strategy.IndexObserver import IndexObserver
from clenow_momentum_strategy.Configuration import INITIAL_CASH

start_date = datetime(2011, 9, 11)
end_date = datetime(2021, 9, 11)

cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)
cerebro.broker.setcash(INITIAL_CASH)

index = bt.feeds.YahooFinanceData(dataname='^OEX',
                                  fromdate=start_date,
                                  todate=end_date,
                                  plot=False)
cerebro.adddata(index)

tickers = pd.read_csv('data/tickers_sp100.csv', header=None)[0].tolist()

for ticker in tickers:
    try:
        stock_data = bt.feeds.YahooFinanceData(dataname=ticker,
                                               fromdate=start_date,
                                               todate=end_date,
                                               plot=False)
        cerebro.adddata(stock_data)
    except:
        print(f"Error while loading {ticker} data.")

cerebro.addobserver(PortfolioObserver)
cerebro.addobserver(IndexObserver)

cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)
cerebro.addstrategy(ClenowMomentumStrategy)

results = cerebro.run()
cerebro.plot()

print(f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%")
print(f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
