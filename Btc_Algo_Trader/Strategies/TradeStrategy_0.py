from Data.dataset import Dataset
from Data.candle import Candle
from Helper.misc import interest
from Helper.datasetMaths import DatasetMaths
from Helper.chart import Chart
from Helper.tradeHandler import TradeHandler
import math

# Trend Indicator: https://www.investopedia.com/articles/trading/07/adx-trend-indicator.asp
# Volatility Indicator: Bollinger Bands
# Volume Indicator: https://www.daytradetheworld.com/trading-blog/the-best-volume-indicators-in-day-trading/
# Momentum Indicator: Stochastic RSI

class BollingerBand:
  def __init__(self, candleSize, sampleSize):
    self.candles = Dataset(candleSize)
    self.closingBids = Dataset(sampleSize)
  
  def update(self, candle):
    c = self.candles
    cb = self.closingBids
    
    c.addData(candle)
    if(c.isMaxLen()):
      highBid = -math.inf
      lowBid = math.inf
      highQuote = None
      lowQuote = None
      openQuote = c.dataset[0].openQuote
      closeQuote = c.dataset[-1].closeQuote
      for ca in c.dataset:
        if(ca.highQuote.bidPrice > highBid): highQuote = ca.highQuote
        if(ca.lowQuote.bidPrice < lowBid): lowQuote = ca.lowQuote
      newCandle = Candle(highQuote, lowQuote, openQuote, closeQuote)
      cb.addData(newCandle.closeQuote.bidPrice)
      self.candles = Dataset(c.len())

  def isReady(self):
    return self.closingBids.isMaxLen()
  
  def high(self):
    cb = self.closingBids
    if(cb.isMaxLen()):
      dm = DatasetMaths()
      return dm.getBBHigh(cb)
    else:
      return None
  
  def mid(self):
    cb = self.closingBids
    if(cb.isMaxLen()):
      dm = DatasetMaths()
      return dm.getBBMid(cb)
    else:
      return None

  def low(self):
    cb = self.closingBids
    if(cb.isMaxLen()):
      dm = DatasetMaths()
      return dm.getBBLow(cb)
    else:
      return None

class StochasticRsi:
  def __init__(self, candleSize, sampleSize, n):
    self.candles = Dataset(candleSize)
    self.highBids = Dataset(sampleSize)
    self.lowBids = Dataset(sampleSize)
    self.nCandles = Dataset(n)
    self.pK = Dataset(30)
    self.brokeLow = False
    self.brokeHigh = False
  
  def update(self, candle):
    c = self.candles
    c.addData(candle)
    if(c.isMaxLen()):
      highBid = -math.inf
      lowBid = math.inf
      highQuote = None
      lowQuote = None
      openQuote = c.dataset[0].openQuote
      closeQuote = c.dataset[-1].closeQuote
      for ca in c.dataset:
        if(ca.highQuote.bidPrice > highBid): highQuote = ca.highQuote
        if(ca.lowQuote.bidPrice < lowBid): lowQuote = ca.lowQuote
      newCandle = Candle(highQuote, lowQuote, openQuote, closeQuote)
      self.highBids.addData(newCandle.highQuote.bidPrice)
      self.lowBids.addData(newCandle.lowQuote.bidPrice)
      self.nCandles.addData(newCandle)
      self.candles = Dataset(c.len())

    if(self.highBids.isMaxLen() and self.lowBids.isMaxLen()):
      C = candle.closeQuote.bidPrice
      LofN = min(self.lowBids.dataset)
      HofN = max(self.highBids.dataset)
      self.pK.addData(100*((C - LofN)/(HofN-LofN)))
      # %K = 100[(C - L of N)/(H of N - L of N)]
      # C = Most Recent Closing Price
      # L of N = Lowest Price Of N Sessions
      # H of N = Highest Price Of N Sessions
      # %D = Three Period Moving Avg Of %K

      # If %D And %K Are Below 20 = Oversold
      # If %D And %K Are Above 80 = Overbought

  def getPK(self):
    return self.pK.dataset[-1]

  def getPD(self):
    dm = DatasetMaths()
    return dm.getMovingAverage(self.pK)

  def isReady(self):
    return self.pK.isMaxLen()

class AwesomeOscillator:
  def __init__(self, candleSize, shortSampleSize, longSampleSize):
    self.candles = Dataset(candleSize)
    self.sMedian = Dataset(shortSampleSize)
    self.lMedian = Dataset(longSampleSize)
    self.ao = Dataset(5)
    self.accel = Dataset(5)
  
  def update(self, candle):
    # M = (H+L)/2
    # AO = SMA(M, 5)-SMA(M, 34)
    # 5 Period Moving Average Of Median - 34 Period Moving Average Of Median
    # Median Is Calculated As M = (H+L)/2
    c = self.candles
    c.addData(candle)
    if(c.isMaxLen()):
      highBid = -math.inf
      lowBid = math.inf
      highQuote = None
      lowQuote = None
      openQuote = c.dataset[0].openQuote
      closeQuote = c.dataset[-1].closeQuote
      for ca in c.dataset:
        if(ca.highQuote.bidPrice > highBid): highQuote = ca.highQuote
        if(ca.lowQuote.bidPrice < lowBid): lowQuote = ca.lowQuote
      newCandle = Candle(highQuote, lowQuote, openQuote, closeQuote)
      median = (newCandle.highQuote.bidPrice + newCandle.lowQuote.bidPrice) / 2
      self.sMedian.addData(median)
      self.lMedian.addData(median)
      dm = DatasetMaths()
      self.ao.addData(dm.getMovingAverage(self.sMedian) - dm.getMovingAverage(self.lMedian))
      self.accel.addData(self.ao.dataset[-1] - dm.getMovingAverage(self.ao))
      self.candles = Dataset(c.len())
  
  def isReady(self):
    return self.sMedian.isMaxLen() and self.lMedian.isMaxLen() and self.ao.isMaxLen()
  
  def getAO(self):
    dm = DatasetMaths()
    return self.ao.dataset[-1]
  
  def getAcceleration(self):
    dm = DatasetMaths()
    return self.ao.dataset[-1] - dm.getMovingAverage(self.ao)

class PercentChange:
  def __init__(self, candleSize, sampleSize):
    self.candles = Dataset(candleSize)
    self.percentChanges = Dataset(sampleSize)
    self.prevCandle = None
  
  def update(self, candle):
    c = self.candles
    
    c.addData(candle)
    if(c.isMaxLen()):
      highBid = -math.inf
      lowBid = math.inf
      highQuote = None
      lowQuote = None
      openQuote = c.dataset[0].openQuote
      closeQuote = c.dataset[-1].closeQuote
      for ca in c.dataset:
        if(ca.highQuote.bidPrice > highBid): highQuote = ca.highQuote
        if(ca.lowQuote.bidPrice < lowBid): lowQuote = ca.lowQuote
      newCandle = Candle(highQuote, lowQuote, openQuote, closeQuote)
      if(self.prevCandle != None):
        self.percentChanges.addData(interest(self.prevCandle.closeQuote.bidPrice, newCandle.closeQuote.bidPrice))
      self.prevCandle = newCandle
      self.candles = Dataset(c.len())

  def isReady(self):
    return self.percentChanges.isMaxLen()
  
  def get(self):
    dm = DatasetMaths()
    return dm.getMovingAverage(self.percentChanges)

class TradeStrategy:
  def __init__(self, isBacktest, btEndDate, btcApi):
    self.isBacktest = isBacktest
    self.btEndDate = btEndDate
    self.stochasticRsi = StochasticRsi(5, 14, 14)
    self.sPercentChange = PercentChange(5, 25)
    self.lPercentChange = PercentChange(5, 250)
    self.chart = Chart()
    self.tradeHandler = TradeHandler(isBacktest, 1000, btcApi, 0.001, 0.0001, 0.0001, 0.000000002)

  def update(self, isTradable, candle):
    date = candle.closeQuote.date
    price = candle.closeQuote.bidPrice

    sRsi = self.stochasticRsi
    sRsi.update(candle)
    spc = self.sPercentChange
    spc.update(candle)
    lpc = self.lPercentChange
    lpc.update(candle)

    if(sRsi.isReady() and spc.isReady() and lpc.isReady()):
      if(isTradable):
        if(self.isBacktest):
          self.chart.addData("Prices", date, price)
          sRsiOversold = sRsi.getPK() < 20
          sRsiOverbought = sRsi.getPK() > 80
          self.chart.addData("Oversold", date, price if sRsiOversold else None)
          self.chart.addData("Overbought", date, price if sRsiOverbought else None)

          s_pc = spc.get()
          l_pc = lpc.get()
          self.chart.addData("Short Percent Change", date, spc.get())
          self.chart.addData("Long Percent Change", date, lpc.get())
          self.chart.addData("Higher Long Percent Change", date, price if l_pc > s_pc else None)
          self.chart.addData("Lower Long Percent Change", date, price if l_pc < s_pc else None)

          if(abs((self.btEndDate - date).total_seconds()) < 180):
            self.chart.show()
            exit()
