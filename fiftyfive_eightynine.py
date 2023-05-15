from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt

# Create a Strategy
class SmaCrossStrategy(bt.Strategy):
    params = (
        ('fast', 55),
        ('slow', 89),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add SMA indicators
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.fast
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.slow
        )

        # Create a crossover indicator
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
            (trade.pnl, trade.pnlcomm)
        )

    def next(self):
      self.log('Close, %.2f' % self.dataclose[0])

      if self.order:  # check if an order is pending
        return

      if not self.position:  # not in the market
        if self.crossover > 0:  # if fast crosses slow to the upside
          self.log('BUY CREATE, %.2f' % self.dataclose[0])
          self.order = self.buy()
      else:  # in the market
        if self.crossover < 0:  # if fast crosses slow to the downside
          self.log('SELL CREATE, %.2f' % self.dataclose[0])
          self.order = self.sell()

    def stop(self):
      self.log(
        '(Fast SMA Period %2d, Slow SMA Period %2d) Ending Value %.2f' %
        (self.params.fast, self.params.slow, self.broker.getvalue()),
        doprint=True
      )

