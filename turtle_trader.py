import backtrader as bt
import yfinance as yf

class TurtleTradingStrategy(bt.Strategy):
    params = (
        ('breakout_period', 20),
        ('stop_loss_period', 10),
    )

    def __init__(self):
        self.order = None
        self.buy_price = None
        self.sell_price = None
        self.buy_comm = None

        self.highest = bt.indicators.Highest(self.data.high(-1), period=self.params.breakout_period)
        self.lowest = bt.indicators.Lowest(self.data.low(-1), period=self.params.stop_loss_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.breakout_period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                self.sell(exectype=bt.Order.Stop, price=self.buy_price - 2*self.atr)
            else:  # Sell
                self.sell_price = order.executed.price
                if self.position:
                    self.buy(exectype=bt.Order.Stop, price=self.sell_price + 2*self.atr)

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.data.close > self.highest:
                self.buy()
            elif self.data.close < self.lowest:
                self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TurtleTradingStrategy)

    # data_df = yf.download("SPY", start="2018-01-01", end="2023-05-15")
    data_df = yf.download("TSLA", period="1mo", interval="60m", prepost=True)
    data = bt.feeds.PandasData(dataname=data_df)
    cerebro.adddata(data)

    cerebro.broker.setcash(1000.0)
    cerebro.broker.setcommission(commission=0.01)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
