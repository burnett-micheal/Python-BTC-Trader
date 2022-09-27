from Data.marketData import MarketData
from Helper.date import Date
from Strategies.TradeStrategy_0 import TradeStrategy

class QuoteHandler:

  def __init__(self, allowedExchange, isBacktest, btStartDate, btEndDate, btcApi):
    self.marketData = MarketData(allowedExchange)
    self.tradeStrategy = TradeStrategy(isBacktest, btEndDate, btcApi)
    self.isBacktest = isBacktest
    self.btStartDate = btStartDate

  def newQuote(self, quoteObj):
    dc = Date()
    respObj = self.marketData.newQuote(quoteObj)
    quote = respObj['quote']
    candle = respObj['candle']

    if(candle is not None):
      nonBacktestCondition = ((dc.utcNow() - quote.date).total_seconds() < 45 and self.isBacktest is False)
      backtestCondition = (self.isBacktest and quote.date > self.btStartDate)
      isTradable = nonBacktestCondition or backtestCondition
      self.tradeStrategy.update(isTradable, candle)