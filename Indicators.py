import backtrader as bt
from scipy.stats import linregress
import numpy as np


class Momentum(bt.Indicator):
    lines = ('trend',)
    params = (('period', 90),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size=self.p.period))
        x = np.arange(len(returns))
        slope, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + slope) ** 252
        self.lines.trend[0] = annualized * (rvalue ** 2)


class IsInIndex(bt.Indicator):
    lines = ('is_in_index',)

    def __init__(self):
        pass

    def next(self):
        # This is not possible to determine with free data set on the Internet.
        # Live list of S&P 100 should be tracked and stored.
        # For testing purposes, we will consider that none of the stocks from the list got out of S&P 100.

        self.lines.is_in_index[0] = True
