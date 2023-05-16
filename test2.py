import yfinance as yf
import backtrader as bt

class MeanReversion(bt.Strategy):
    params = (
        ('period', 13),
        ('devfactor', 2.5),
        ('size', 3),
        ('stop_loss', 0.07),
        ('take_profit1', 0.02),
        ('take_profit2', 0.03),
        ('take_profit3', 0.1),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None
        self.price = None
        self.comm = None
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:  # Sell
                self.price = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f"OPERATION PROFIT, GROSS {trade.pnl}, NET {trade.pnlcomm}")

    def next(self):
        if self.order:
            return

        if not self.position:  # not in the market
            if self.data.close < self.bbands.lines.bot:  # if close price is below lower bollinger band
                self.order = self.buy(size=self.params.size)  # enter long
        else:  # in the market
            if self.data.close > self.bbands.lines.top:  # if close price is above upper bollinger band
                self.order = self.sell(size=self.position.size)  # exit long
            elif self.price is not None:
                if self.data.close <= self.price * (1.0 - self.params.stop_loss):  # stop loss
                    self.order = self.sell(size=self.position.size)
                elif self.data.close >= self.price * (1.0 + self.params.take_profit1) and self.position.size == 3:  # take profit level 1
                    self.order = self.sell(size=1)
                elif self.data.close >= self.price * (1.0 + self.params.take_profit2) and self.position.size == 2:  # take profit level 2
                    self.order = self.sell(size=1)
                elif self.data.close >= self.price * (1.0 + self.params.take_profit3) and self.position.size == 1:  # take profit level 3
                    self.order = self.sell(size=1)

if __name__ == "__main__":

    # Create a backtest instance
    cerebro = bt.Cerebro()

    # Add the strategy to the backtest instance
    cerebro.addstrategy(MeanReversion)

    # Import the data using yfinance
    # data_df = yf.download("SPY", start="2018-01-01", end="2023-05-15")
    data_df = yf.download("SPY", period="5y", interval="1d", prepost=True)

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
    # cerebro.run(maxcpus=1)
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()