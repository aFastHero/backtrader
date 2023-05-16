import backtrader as bt
import yfinance as yf

class RsiDivergenceStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_divergence', 5),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.rsi_period)
        self.rsi_prev = self.rsi(-1)  # RSI value of the previous period
        self.price_prev = self.data.close(-1)  # Close price of the previous period

    def next(self):
        rsi_diff = self.rsi - self.rsi_prev
        price_diff = self.data.close - self.price_prev

        # Bearish divergence
        if self.rsi > self.params.rsi_upper and price_diff > 0 and rsi_diff < -self.params.rsi_divergence:
            if self.position:
                self.sell()
            else:
                self.sell()

        # Bullish divergence
        elif self.rsi < self.params.rsi_lower and price_diff < 0 and rsi_diff > self.params.rsi_divergence:
            if self.position:
                self.buy()
            else:
                self.buy()


if __name__ == '__main__':

  # Create a cerebro
  cerebro = bt.Cerebro()

  # Add the strategy to cerebro
  cerebro.addstrategy(RsiDivergenceStrategy)

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
