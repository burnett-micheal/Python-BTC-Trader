from Helper.misc import getQuoteObjectsInDateRange, streamQuotes
from Helper.date import Date
from Helper.btcApi import BtcApi
from Helper.quoteHandler import QuoteHandler

def main():
  allowedExchange = "CBSE"
  isBacktest = True
  dc = Date()
  btStartDate = dc.date(2021, 12, 25, 0, 0, 0, 0)
  btEndDate = dc.date(2021, 12, 27, 6, 0, 0, 0)
  btcApi = BtcApi("PKW5P6SMLRBVQLK6DYQ3", "7KzMngilx8lrbRrCEbWrW4dcK660AOdzHZOWIa9J", "https://paper-api.alpaca.markets", "wss://stream.data.alpaca.markets/v1beta1/crypto?exchanges="+allowedExchange, "https://data.alpaca.markets", allowedExchange)
  quoteHandler = QuoteHandler(allowedExchange, isBacktest, btStartDate, btEndDate, btcApi)

  if(isBacktest):
    quoteObjects = getQuoteObjectsInDateRange(dc.subDays(btStartDate, 7), btEndDate, allowedExchange, btcApi)
    for qObj in quoteObjects: quoteHandler.newQuote(qObj)
    quoteObjects = []
  else:
    quoteObjects = []
    while(len(quoteObjects) == 0 or (dc.utcNow() - dc.rfc2date(quoteObjects[-1]['t'])).total_seconds() > 30):
      qStartDate = dc.addSeconds(dc.rfc2date(quoteObjects[-1]['t']), 1) if len(quoteObjects) > 0 else dc.subDays(dc.utcNow(), 7)
      quoteObjects.extend(getQuoteObjectsInDateRange(qStartDate, dc.utcNow(), allowedExchange, btcApi))
    for qObj in quoteObjects: quoteHandler.newQuote(qObj)
    quoteObjects = []
    print("Started Streaming")
    streamQuotes(btcApi, allowedExchange, quoteHandler)

main()