from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt

class SmaCross(bt.SignalStrategy):
  params = (
    ('fast', 55),
    ('slow', 89),
    ('printlog', False),
  )

  def __init__(self):
    sma1, sma2 = bt.ind.SMA(period=self.params.fast), bt.ind.SMA(period=self.params.slow)
    crossover = bt.ind.CrossOver(sma1, sma2)
    self.signal_add(bt.SIGNAL_LONGSHORT, crossover)