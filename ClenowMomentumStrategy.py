import backtrader as bt
from Indicators import Momentum, IsInIndex

TOP_STOCKS_PCT = 0.2
STOCK_MOVING_AVERAGE = 100
INDEX_MOVING_AVERAGE = 200


class ClenowMomentumStrategy(bt.Strategy):

    def __init__(self):
        self.inds = {}
        self.index = self.datas[0]
        self.stocks = self.datas[1:]

        self.index_sma200 = bt.indicators.SimpleMovingAverage(self.index, period=INDEX_MOVING_AVERAGE)

        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d, period=90)
            self.inds[d]["sma100"] = bt.indicators.SimpleMovingAverage(d, period=STOCK_MOVING_AVERAGE)
            self.inds[d]["atr20"] = bt.indicators.ATR(d, period=20)
            self.inds[d]["is_in_index"] = IsInIndex(d)

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()

    def next(self):
        if len(self) == INDEX_MOVING_AVERAGE:
            self.__initialize_portfolio()
        elif len(self) > INDEX_MOVING_AVERAGE:
            if self.__week_passed():
                self.__portfolio_rebalance()
            if self.__two_weeks_passed():
                self.__positions_rebalance()

    def notify_trade(self, trade):
        if trade.status == 0:
            status = "Created"
        elif trade.status == 1:
            buy_sell = "Bought" if trade.size>0 else "Sold"
            print(f"{buy_sell} {abs(trade.size)} of {trade.getdataname()} shares for price {trade.price}.")

        if trade.isclosed:
            print (f"Closed position for {trade.getdataname()}")

    def __portfolio_rebalance(self):
        self.__update_rankings()
        self.__sell_stocks()
        if self.__is_index_in_positive_trend():
            self.__buy_stocks()

    def __positions_rebalance(self):
        if self.__is_index_in_positive_trend():
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
        for i, d in enumerate(self.rankings):
            if self.getposition(d).size:
                if i > len(self.rankings) * TOP_STOCKS_PCT or \
                        d < self.inds[d]["sma100"] or \
                        self.inds[d]["is_in_index"] == False:
                    self.close(d)

    def __buy_stocks(self):
        cash = self.broker.get_cash()
        for i, d in enumerate(self.rankings[:int(len(self.rankings) * TOP_STOCKS_PCT)]):
            cash = self.broker.get_cash()
            if cash <= 0:
                break
            if not self.getposition(d).size:
                self.buy(d, size=self.__position_size(d))

    def __is_index_in_positive_trend(self):
        return self.index > self.index_sma200

    def __is_stock_in_positive_trend(self, stock):
        return stock > self.inds[stock]["sma100"]

    def __is_stock_in_index(self, stock):
        return self.inds[stock]["is_in_index"] == True

    def __position_size(self, stock):
        return int(self.broker.get_value() * 0.001 / self.inds[stock]["atr20"])

    def __initialize_portfolio(self):
        if self.__is_index_in_positive_trend():
            self.__update_rankings()
            self.__buy_stocks()

