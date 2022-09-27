from Helper.date import Date

class Quote:
  def __init__(self, rfcDate, exchange, askPrice, askSize, bidPrice, bidSize):
      self.date = Date().rfc2date(rfcDate)
      self.exchange = exchange
      self.askPrice = askPrice
      self.askSize = askSize
      self.bidPrice = bidPrice
      self.bidSize = bidSize