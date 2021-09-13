from backtrader import Observer


class IndexObserver(Observer):
    _stclock = True


    alias = ('S&P 100 prices and momentum',)
    lines = ('index', 'index_momentum')

    plotinfo = dict(plot=True, subplot=True)


    def next(self):
        self.lines.index[0] = self._owner.index[0]
        self.lines.index_momentum[0] = self._owner.index_sma[0]
