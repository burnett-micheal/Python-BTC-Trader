from Data.candle import Candle
from Data.quote import Quote
from Helper.date import Date
from pandas import read_excel
import xlsxwriter
import os

# Saves Todays Quotes
# Each Minute Converts Quotes Array To A Candle And Clears Quotes Array - This is done in newQuote
# Each Day Converts Candles Array To A File And Clears Candles Array - This is done in newCandle

class MarketData:
  quotes = []
  candles = []

  def __init__(self, allowedExchange):
      self.allowedExchange = allowedExchange
  
  def newQuote(self, quoteObj):
    quote = Quote(quoteObj['t'], quoteObj['x'], quoteObj['ap'], quoteObj['as'], quoteObj['bp'], quoteObj['bs'])
    
    newCandle = None
    if(len(self.quotes) > 0):
      if(self.quotes[-1].date.minute != quote.date.minute):
        highQuote = None
        lowQuote = None
        openQuote = None
        closeQuote = None
        for q in self.quotes:
          if(highQuote is None): highQuote = lowQuote = openQuote = closeQuote = q
          else:
            if(q.bidPrice > highQuote.bidPrice): highQuote = q
            elif(q.bidPrice < lowQuote.bidPrice): lowQuote = q
            if(q.date < openQuote.date): openQuote = q
            elif(q.date > closeQuote.date): closeQuote = q
        newCandle = self.newCandle(highQuote, lowQuote, openQuote, closeQuote)
        
        self.quotes = []
    
    self.quotes.append(quote)
    return {'quote': quote, 'candle': newCandle}

  def newCandle(self, highQuote, lowQuote, openQuote, closeQuote):
    candle = Candle(highQuote, lowQuote, openQuote, closeQuote)
    if(len(self.candles) > 0):
      if(candle.closeQuote.date.day != self.candles[-1].closeQuote.date.day):
        fileName = self.candles[-1].closeQuote.date.strftime("%m-%d-%Y")+".xlsx"
        filePath = "./Btc_Quotes_v2/"+self.allowedExchange+"/"+fileName
        if(os.path.isfile(filePath) is False):
          print("Writing File: ", filePath)
          workbook = xlsxwriter.Workbook(filePath)
          worksheet = workbook.add_worksheet()
          row = 0
          worksheet.write_row(row, 0, ['Time', 'High Quote Date', 'High Quote Exchange', 'High Quote Bid Price', 'High Quote Bid Size', 'High Quote Ask Price', 'High Quote Ask Size', 'Low Quote Date', 'Low Quote Exchange', 'Low Quote Bid Price', 'Low Quote Bid Size', 'Low Quote Ask Price', 'Low Quote Ask Size', 'Open Quote Date', 'Open Quote Exchange', 'Open Quote Bid Price', 'Open Quote Bid Size', 'Open Quote Ask Price', 'Open Quote Ask Size', 'Close Quote Date', 'Close Quote Exchange', 'Close Quote Bid Price', 'Close Quote Bid Size', 'Close Quote Ask Price', 'Close Quote Ask Size'])
          for c in self.candles:
            row += 1
            hq = c.highQuote
            lq = c.lowQuote
            oq = c.openQuote
            cq = c.closeQuote
            dc = Date()
            timeStr = oq.date.strftime("%H:%M")
            worksheet.write_row(row, 0, [timeStr, dc.date2rfc(hq.date), hq.exchange, hq.bidPrice, hq.bidSize, hq.askPrice, hq.askSize, dc.date2rfc(lq.date), lq.exchange, lq.bidPrice, lq.bidSize, lq.askPrice, lq.askSize, dc.date2rfc(oq.date), oq.exchange, oq.bidPrice, oq.bidSize, oq.askPrice, oq.askSize, dc.date2rfc(cq.date), cq.exchange, cq.bidPrice, cq.bidSize, cq.askPrice, cq.askSize])
          workbook.close()

        self.candles = []

    self.candles.append(candle)
    return candle

  def getCandles(self, startDate, endDate):
    dc = Date()
    if(startDate >= endDate): Exception("Start Date Is Not Before End Date")
    if(startDate < dc.now()): Exception("Start Date Is After Current Date")
    if(endDate > dc.addMinutes(dc.now(), 1)): Exception("End Date Is After Current Date")

    curDate = startDate
    candles = []

    fileName = curDate.strftime("%m-%d-%Y")+".xlsx"
    filePath = "./Btc_Quotes_v2/"+self.allowedExchange+"/"+fileName

    while os.path.isfile(filePath) and curDate < endDate:
      df = read_excel(filePath)
      for index, rows in df.iterrows():
        if(dc.rfc2date(rows['Open Quote Date']) >= curDate and dc.rfc2date(rows['Close Quote Date']) <= endDate):
          highQuote = Quote(rows['High Quote Date'], rows['High Quote Exchange'], rows['High Quote Bid Price'], rows['High Quote Bid Size'], rows['High Quote Ask Price'], rows['High Quote Ask Size'])
          lowQuote = Quote(rows['Low Quote Date'], rows['Low Quote Exchange'], rows['Low Quote Bid Price'], rows['Low Quote Bid Size'], rows['Low Quote Ask Price'], rows['Low Quote Ask Size'])
          openQuote = Quote(rows['Open Quote Date'], rows['Open Quote Exchange'], rows['Open Quote Bid Price'], rows['Open Quote Bid Size'], rows['Open Quote Ask Price'], rows['Open Quote Ask Size'])
          closeQuote = Quote(rows['Close Quote Date'], rows['Close Quote Exchange'], rows['Close Quote Bid Price'], rows['Close Quote Bid Size'], rows['Close Quote Ask Price'], rows['Close Quote Ask Size'])
          candle = Candle(highQuote, lowQuote, openQuote, closeQuote)
          candles.append(candle)
      
      curDate = dc.addDays(curDate, 1)
      curDate = dc.date(curDate.year, curDate.month, curDate.day, 0, 0, 0, 0)
      fileName = curDate.strftime("%m-%d-%Y")+".xlsx"
      filePath = "./Btc_Quotes_v2/"+self.allowedExchange+"/"+fileName
    
    if(curDate < endDate):
      for c in self.candles:
        if(c.openQuote.date >= curDate and c.closeQuote.date <= endDate): 
          candles.append(c)
          curDate = c.closeQuote.date
    
    return candles

