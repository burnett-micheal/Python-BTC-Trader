from Data.quote import Quote

class Candle:
  def __init__(self, highQuote, lowQuote, openQuote, closeQuote):
    if(isinstance(highQuote, Quote) and isinstance(lowQuote, Quote) and isinstance(openQuote, Quote) and isinstance(closeQuote, Quote)):
      self.highQuote = highQuote
      self.lowQuote = lowQuote
      self.openQuote = openQuote
      self.closeQuote = closeQuote
    else:
      Exception("Candle Provided With Invalid Values, Not All Quote Parameters Are Quote Classes")