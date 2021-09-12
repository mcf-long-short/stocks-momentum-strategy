import backtrader as bt
from Indicators import Momentum, IsInIndex

TOP_STOCKS_PCT = 0.2
MAXIMUM_GAP = 0.15
STOCK_MOVING_AVERAGE = 100
INDEX_MOVING_AVERAGE = 200
GAP_MOVING_AVERAGE = 90

class ClenowMomentumStrategy(bt.Strategy):

    def __init__(self):
        self.inds = {}
        self.index = self.datas[0]
        self.stocks = self.datas[1:]
        self.portfolio_initialized = False
        self.cash = self.broker.get_cash()

        self.index_sma200 = bt.indicators.SimpleMovingAverage(self.index, period=INDEX_MOVING_AVERAGE)

        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d, period=90)
            self.inds[d]["sma100"] = bt.indicators.SimpleMovingAverage(d, period=STOCK_MOVING_AVERAGE)
            self.inds[d]["sma90"] = bt.indicators.SimpleMovingAverage(d, period=GAP_MOVING_AVERAGE)
            self.inds[d]["atr20"] = bt.indicators.ATR(d, period=20)
            self.inds[d]["is_in_index"] = IsInIndex(d)

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()

    def next(self):
        self.cash = self.broker.get_cash()
        if len(self) >= INDEX_MOVING_AVERAGE:
            if not self.portfolio_initialized:
                self.__initialize_portfolio()
            else:
                if self.__week_passed():
                    print (self.broker.get_cash())
                    self.__portfolio_rebalance()
                if self.__two_weeks_passed():
                    self.__positions_rebalance()

    def __portfolio_rebalance(self):
        self.__update_rankings()
        self.__sell_stocks()
        if self.__is_index_in_positive_trend():
            self.__buy_stocks()

    def __positions_rebalance(self):
        for i, d in enumerate(self.rankings[:int(len(self.rankings) * TOP_STOCKS_PCT)]):
            cash = self.broker.get_cash()
            if cash <= 0:
                break
            self.order_target_size(d, self.__position_size(d))

    def __week_passed(self):
        return len(self) % 5 == 0

    def __two_weeks_passed(self):
        return len(self) % 10 == 0

    def __update_rankings(self):
        self.rankings = list(filter(lambda d: len(d) > 100, self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["momentum"][0])

    def __sell_stocks(self):
        for i, stock in enumerate(self.rankings):
            position_size = self.getposition(stock).size
            position_price = self.getposition(stock).price
            if position_size:
                if i > len(self.rankings) * TOP_STOCKS_PCT or \
                        not self.__is_stock_in_positive_trend(stock) or \
                        not self.__is_stock_in_index(stock) or \
                        self.__stock_exceeds_gap(stock):

                    value = position_size * position_price
                    self.close(stock)
                    print(f"Closing position {stock._dataname} by selling {position_size} shares.")
                    self.cash = self.cash + value

    def __buy_stocks(self):
        if self.cash > 0:
            for stock in self.rankings[:int(len(self.rankings) * TOP_STOCKS_PCT)]:
                if not self.getposition(stock).size and \
                        self.__is_stock_in_positive_trend(stock) and \
                        not self.__stock_exceeds_gap(stock):

                    size = self.__position_size(stock)
                    price = stock[0]
                    value = size * price
                    if self.cash >= value:
                        print(f"Bought {size} of {stock._dataname} shares for price {stock[0]}.")
                        self.buy(stock, size=size)
                        self.cash = self.cash - value
                    else:
                        break

    def __is_index_in_positive_trend(self):
        return self.index > self.index_sma200

    def __is_stock_in_positive_trend(self, stock):
        return stock > self.inds[stock]["sma100"]

    def __is_stock_in_index(self, stock):
        return self.inds[stock]["is_in_index"] == True

    def __stock_exceeds_gap(self, stock, initial=False):
        if initial:
            abs((stock[0]-self.inds[stock]["sma90"])/self.inds[stock]["sma90"]) > MAXIMUM_GAP
        else:
            abs((stock[0] - stock[-1]) / stock[-1]) > MAXIMUM_GAP

    def __position_size(self, stock):
        return int(self.broker.get_value() * 0.001 / self.inds[stock]["atr20"])

    def __initialize_portfolio(self):
        if self.__is_index_in_positive_trend():
            self.__update_rankings()

            for stock in self.rankings:
                if self.__is_stock_in_positive_trend(stock) and not self.__stock_exceeds_gap(stock, True):
                    size = self.__position_size(stock)
                    price = stock[0]
                    value = size * price
                    if self.cash >= value:
                        print (f"Bought {size} of {stock._dataname} shares for price {stock[0]}.")
                        self.buy(stock, size=size)
                        self.cash = self.cash - value
                    else:
                        break
            self.portfolio_initialized = True

