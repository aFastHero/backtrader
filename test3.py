import yfinance as yf
import backtrader as bt

class FibonacciRetracement(bt.Strategy):
    params = (
        ('period', 21),
        ('level1', 38.2),
        ('level2', 61.8),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.high = bt.indicators.Highest(self.data.high, period=self.p.period)
        self.low = bt.indicators.Lowest(self.data.low, period=self.p.period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] <= self.low[0] + (self.high[0] - self.low[0]) * self.p.level2 / 100:
                self.order = self.buy()
        else:
            if self.dataclose[0] >= self.low[0] + (self.high[0] - self.low[0]) * self.p.level1 / 100:
                self.order = self.sell()

if __name__ == "__main__":

    # Create a backtest instance
    cerebro = bt.Cerebro()

    # Add the strategy to the backtest instance
    cerebro.addstrategy(FibonacciRetracement)

    # Import the data using yfinance
    # data_df = yf.download("SPY", start="2018-01-01", end="2023-05-15")
    data_df = yf.download("SPY", period="6mo", interval="1d", prepost=True)

    # Convert the data into a backtrader feed
    data = bt.feeds.PandasData(dataname=data_df)

    # Add the data to the backtest instance
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.01)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
