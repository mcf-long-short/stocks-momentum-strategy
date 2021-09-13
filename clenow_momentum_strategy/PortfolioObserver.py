from backtrader import Observer

class PortfolioObserver(Observer):
    _stclock = True

    params = (
        ('fund', None),
    )

    alias = ('Portfolio Value',)
    lines = ('cash', 'value', 'portfolio')

    plotinfo = dict(plot=True, subplot=True)

    def start(self):
        if self.p.fund is None:
            self._fundmode = self._owner.broker.fundmode
        else:
            self._fundmode = self.p.fund

        if self._fundmode:
            self.plotlines.cash._plotskip = True
            self.plotlines.value._name = 'FundValue'

    def next(self):
        if not self._fundmode:
            self.lines.value[0] = value = self._owner.broker.getvalue()
            self.lines.cash[0] = cash = self._owner.broker.getcash()
            self.lines.portfolio[0] = value - cash
        else:
            self.lines.value[0] = self._owner.broker.fundvalue