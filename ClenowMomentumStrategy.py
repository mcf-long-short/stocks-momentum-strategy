import backtrader as bt
from Indicators import Momentum, IsInIndex

TOP_STOCKS_PCT = 0.2
STOCK_MOVING_AVERAGE = 100
INDEX_MOVING_AVERAGE = 200


class ClenowMomentumStrategy(bt.Strategy):

    def __init__(self):
        self.i = 0
        self.inds = {}
        self.index = self.datas[0]
        self.stocks = self.datas[1:]

        self.index_sma200 = bt.indicators.SimpleMovingAverage(self.index.adjclose, period=INDEX_MOVING_AVERAGE)

        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d.adjclose, period=90)
            self.inds[d]["sma100"] = bt.indicators.SimpleMovingAverage(d.adjclose, period=STOCK_MOVING_AVERAGE)
            self.inds[d]["atr20"] = bt.indicators.ATR(d, period=20)

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()

    def next(self):
        if self.__week_passed():
            self.portfolio_rebalance()
        if self.__two_weeks_passed():
            self.positions_rebalance()
        self.i += 1

    def portfolio_rebalance(self):
        self.__update_rankings()
        self.__sell_stocks()
        if self.__is_index_in_positive_trend():
            self.__buy_stocks()

    def positions_rebalance(self):
        if self.index < self.index_sma200:
            return

        # rebalance all stocks
        for i, d in enumerate(self.rankings[:int(len(self.rankings) * TOP_STOCKS_PCT)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[d]["atr20"]
            self.order_target_size(d, size)

    def __week_passed(self):
        return self.i % 5 == 0

    def __two_weeks_passed(self):
        return self.i % 10 == 0

    def __update_rankings(self):
        self.rankings = list(filter(lambda d: len(d) > 100, self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["momentum"][0])

    def __sell_stocks(self):
        for i, d in enumerate(self.rankings):
            if self.getposition(self.data).size:
                if i > len(self.rankings) * TOP_STOCKS_PCT or d < self.inds[d]["sma100"]:
                    self.close(d)

    def __buy_stocks(self):
        for i, d in enumerate(self.rankings[:int(len(self.rankings) * TOP_STOCKS_PCT)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(self.data).size:
                size = value * 0.001 / self.inds[d]["atr20"]
                self.buy(d, size=size)

    def __is_index_in_positive_trend(self):
        return self.index > self.index_sma200