import backtrader as bt
from clenow_momentum_strategy.Indicators import Momentum, IsInIndex

from clenow_momentum_strategy.Configuration import \
    TOP_STOCKS_PCT, \
    MAXIMUM_GAP, \
    STOCK_MOVING_AVERAGE, \
    INDEX_MOVING_AVERAGE, \
    GAP_MOVING_AVERAGE, \
    MOMENTUM_PERIOD


class ClenowMomentumStrategy(bt.Strategy):

    def __init__(self):
        self.inds = {}
        self.index = self.datas[0]
        self.stocks = self.datas[1:]
        self.portfolio_initialized = False
        self.cash = self.broker.get_cash()

        self.index_sma = bt.indicators.SimpleMovingAverage(self.index.close, period=INDEX_MOVING_AVERAGE)

        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d, period=MOMENTUM_PERIOD)
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
                    print ("Portfolio Rebalancing")
                    self.__portfolio_rebalance()
                    print ("")
                if self.__two_weeks_passed():
                    print("Position Rebalancing")
                    self.__positions_rebalance()
                    print("")

    def __portfolio_rebalance(self):
        self.__update_rankings()
        self.__sell_stocks()
        if self.__is_index_in_positive_trend():
            self.__buy_stocks()

    def __positions_rebalance(self):
        for stock in self.rankings:
            position_size = self.getposition(stock).size
            new_position_size = self.__position_size(stock)
            price = stock[0]

            if new_position_size > position_size:
                buy_size = new_position_size - position_size
                value = buy_size * price
                if self.cash >= value:
                    self.buy(stock, size=buy_size)
                    print(f"Bought {buy_size} of {stock._dataname} shares for price {price}.")
                    self.cash = self.cash - value
                else:
                    continue
            elif new_position_size < position_size:
                sell_size = position_size - new_position_size
                value = sell_size * price
                self.sell(stock, size=sell_size)
                print(f"Sold {sell_size} of {stock._dataname} shares for price {price}.")
                self.cash = self.cash + value
            else:
                pass

    def __week_passed(self):
        return len(self) % 5 == 0

    def __two_weeks_passed(self):
        return len(self) % 10 == 0

    def __update_rankings(self):
        self.rankings = list(filter(lambda d: len(d) > STOCK_MOVING_AVERAGE, self.stocks))
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
                    print(f"Closing position {stock._dataname} by selling {abs(position_size)} shares.")
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
        return self.index > self.index_sma

    def __is_stock_in_positive_trend(self, stock):
        return stock > self.inds[stock]["sma100"]

    def __is_stock_in_index(self, stock):
        return self.inds[stock]["is_in_index"] == True

    def __stock_exceeds_gap(self, stock, initial=False):
        if initial:
            return abs((stock[0]-self.inds[stock]["sma90"])/self.inds[stock]["sma90"]) > MAXIMUM_GAP
        else:
            return abs((stock[0] - stock[-1]) / stock[-1]) > MAXIMUM_GAP

    def __position_size(self, stock):
        return int(self.broker.get_value() * 0.001 / self.inds[stock]["atr20"])

    def __initialize_portfolio(self):
        if self.__is_index_in_positive_trend():
            print("Initializing Portfolio.")
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
            print("")

