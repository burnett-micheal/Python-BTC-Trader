import os
import json
import math
from Helper.date import Date
from pandas import read_excel

def getQuoteObjectsInDateRange(startDate, endDate, allowedExchange, btcApi):
  dataCurDate = startDate 
  quotes = []
  dc = Date()
  while(endDate > dataCurDate):
    fileName = dataCurDate.strftime("%m-%d-%Y")+".xlsx"
    filePath = "./Btc_Quotes_v2/"+allowedExchange+"/"+fileName
    if(os.path.isfile(filePath) is False):
      _endDate = dc.addDays(dataCurDate, 1) if endDate > dc.addDays(dataCurDate, 1) else endDate
      response = btcApi.btcHistory(dataCurDate, _endDate, 10000)
      if(response['quotes'] is not None):
        quotes.extend(response['quotes'])
        npt = response['next_page_token']
        while(npt is not None):
          response = btcApi.btcHistory(dataCurDate, _endDate, 10000, npt)
          quotes.extend(response['quotes'])
          npt = response['next_page_token']
    else:
      fileName = dataCurDate.strftime("%m-%d-%Y")+".xlsx"
      filePath = "./Btc_Quotes_v2/"+allowedExchange+"/"+fileName
      df = read_excel(filePath)
      for index, rows in df.iterrows():
        if(dc.rfc2date(rows['Open Quote Date']) >= startDate and dc.rfc2date(rows['Close Quote Date']) <= endDate):
          def newQuoteObj(t,x,bp,bs,ap,_as): return {'t':t, 'x':x, 'bp':bp, 'bs':bs, 'ap':ap, 'as':_as}
          highQuote = newQuoteObj(rows['High Quote Date'], rows['High Quote Exchange'], rows['High Quote Bid Price'], rows['High Quote Bid Size'], rows['High Quote Ask Price'], rows['High Quote Ask Size'])
          lowQuote = newQuoteObj(rows['Low Quote Date'], rows['Low Quote Exchange'], rows['Low Quote Bid Price'], rows['Low Quote Bid Size'], rows['Low Quote Ask Price'], rows['Low Quote Ask Size'])
          openQuote = newQuoteObj(rows['Open Quote Date'], rows['Open Quote Exchange'], rows['Open Quote Bid Price'], rows['Open Quote Bid Size'], rows['Open Quote Ask Price'], rows['Open Quote Ask Size'])
          closeQuote = newQuoteObj(rows['Close Quote Date'], rows['Close Quote Exchange'], rows['Close Quote Bid Price'], rows['Close Quote Bid Size'], rows['Close Quote Ask Price'], rows['Close Quote Ask Size'])
          quote2 = None
          quote3 = None
          if(dc.rfc2date(highQuote['t']) > dc.rfc2date(lowQuote['t'])):
            quote2 = lowQuote
            quote3 = highQuote
          else:
            quote2 = highQuote
            quote3 = lowQuote
          quotes.extend([openQuote, quote2, quote3, closeQuote])
      dataCurDate = dc.date(dataCurDate.year, dataCurDate.month, dataCurDate.day, 0, 0, 0, 0)

    dataCurDate = dc.addDays(dataCurDate, 1)
  
  return quotes

def streamQuotes(btcApi, allowedExchange, quoteHandler):
  ws = btcApi.websocket()
  while True:
    try:
      dataArray = json.loads(ws.recv())
      for data in dataArray:
        date = data['t']
        askSize = data['as']
        askPrice = data['ap']
        bidSize = data['bs']
        bidPrice = data['bp']
        exchange = data['x']
        symbol = data['S']
        if(symbol != "BTCUSD"):
          print("Websocket Symbol Does Not Equal BTCUSD")
          exit()
        if(exchange != allowedExchange):
          print("Websocket Exchange Does Not Equal Allowed Exchange")
          exit()
        qObj = {'t': date, 'x': exchange, 'as': askSize, 'ap': askPrice, 'bs': bidSize, 'bp': bidPrice}
        quoteHandler.newQuote(qObj)
    except Exception as e:
      print("An Error Occured In Websocket: ", e)
      ws = btcApi.websocket()

def interest(oldPrice, newPrice):
  mod = -1 if oldPrice > newPrice else 1
  percentChange = mod * (abs(newPrice - oldPrice) / oldPrice)
  percentChange = math.floor(percentChange * 1000000)/1000000
  return percentChange