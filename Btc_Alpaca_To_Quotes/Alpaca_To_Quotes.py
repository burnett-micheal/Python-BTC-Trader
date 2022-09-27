from time import sleep
import requests
from date import Date
import xlsxwriter
import os

# A Few Bugs In This Script:
# Historical Data Overwrite After A Non-File Due To No Quotes That Day
# I Recommend Checking If Quotes Exists For Non-Files Between Start Date And End Date

ALPACA_API_KEY = "PKW5P6SMLRBVQLK6DYQ3"
ALPACA_SECRET_KEY = "7KzMngilx8lrbRrCEbWrW4dcK660AOdzHZOWIa9J"
HISTORY_URL = "https://data.alpaca.markets"

def btcHistory(startDate, endDate=None, quoteLimit=None, nextPageToken=None):
  dc = Date()
  reqUrl = HISTORY_URL+"/v1beta1/crypto/BTCUSD/quotes?start=" + dc.date2rfc(startDate)
  if(endDate is not None): reqUrl += "&end=" + dc.date2rfc(endDate)
  if(quoteLimit is not None): reqUrl += "&limit=" + str(quoteLimit)
  if(nextPageToken is not None): reqUrl += "&page_token=" + nextPageToken
  reqHeaders = {"APCA-API-KEY-ID":ALPACA_API_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET_KEY}
  r = requests.get(reqUrl, headers=reqHeaders)
  if(r.status_code != 200 and r.status_code != 404):
    print(reqUrl)
    print(r)
    raise Exception("Bad Response Code")
  return r.json()

dc = Date()
startDate = dc.date(2021, 4, 3, 0, 0, 0, 0)
while(os.path.isfile("./Btc_Quotes/"+dc.dateStr(startDate)+".xlsx") is True): startDate = dc.addDays(startDate, 1)
endDate = dc.date(2022, 4, 3, 0, 0, 0, 0)
if(startDate >= endDate): Exception("Either All Files Exist Or Your Start Date Is After The End Date")
print(startDate, endDate)
curDate = startDate
nextPageToken = None
quotes = {} 
# { '03/04/2021': {'00:00': { 'High Quote': , 'Low Quote': , 'Open Quote': , 'Close Quote': } } }
# Price = { 'Date': , 'Exchange': , 'Ask Price': , 'Bid Price': , 'Ask Size': , 'Bid Size': }
dateStr = None
timeStr = None
candleQuotes = [] # { 'Date': , 'Exchange': , 'Bid Price': , 'Bid Size': , 'Ask Price': , 'Ask Size': } 

while(True):
  r = None
  if(nextPageToken is None):
    r = btcHistory(startDate, endDate, 10000)
  else:
    r = btcHistory(startDate, endDate, 10000, nextPageToken)
  nextPageToken = r['next_page_token']
  if(r['symbol'] != 'BTCUSD'): Exception('Symbol Is Not BTCUSD')
  
  for quote in r['quotes']:
    date = dc.rfc2date(quote['t'])
    if(dateStr is None or timeStr is None): 
      dateStr = dc.dateStr(date)
      timeStr = dc.timeStr(date)
    elif(dateStr != dc.dateStr(date) or timeStr != dc.timeStr(date)):
      highQuote = None
      lowQuote = None
      openQuote = None
      closeQuote = None
      
      for i, candleQuote in enumerate(candleQuotes):
        if(i == 0): highQuote = lowQuote = openQuote = closeQuote = candleQuote
        if(candleQuote['Bid Price'] > highQuote['Bid Price']): highQuote = candleQuote
        if(candleQuote['Bid Price'] < lowQuote['Bid Price']): lowQuote = candleQuote
        if(candleQuote['Date'] < openQuote['Date']): openQuote = candleQuote
        if(candleQuote['Date'] > closeQuote['Date']): closeQuote = candleQuote
      
      if(dateStr not in quotes): quotes[dateStr] = {}
      quotes[dateStr][timeStr] = {'High Quote': highQuote, 'Low Quote': lowQuote, 'Open Quote': openQuote, 'Close Quote': closeQuote}
      candleQuotes = []

      if(dateStr != dc.dateStr(date)):
        workbook = xlsxwriter.Workbook('./Btc_Quotes/'+dateStr+'.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write_row(row, 0, ['Time', 'High Quote Date', 'High Quote Exchange', 'High Quote Bid Price', 'High Quote Bid Size', 'High Quote Ask Price', 'High Quote Ask Size', 'Low Quote Date', 'Low Quote Exchange', 'Low Quote Bid Price', 'Low Quote Bid Size', 'Low Quote Ask Price', 'Low Quote Ask Size', 'Open Quote Date', 'Open Quote Exchange', 'Open Quote Bid Price', 'Open Quote Bid Size', 'Open Quote Ask Price', 'Open Quote Ask Size', 'Close Quote Date', 'Close Quote Exchange', 'Close Quote Bid Price', 'Close Quote Bid Size', 'Close Quote Ask Price', 'Close Quote Ask Size'])
        for key in quotes[dateStr]:
          row += 1
          candle = quotes[dateStr][key]
          highQuote = candle['High Quote']
          lowQuote = candle['Low Quote']
          openQuote = candle['Open Quote']
          closeQuote = candle['Close Quote']
          worksheet.write_row(row, 0, [key, dc.date2rfc(highQuote['Date']), highQuote['Exchange'], highQuote['Bid Price'], highQuote['Bid Size'], highQuote['Ask Price'], highQuote['Ask Size'], dc.date2rfc(lowQuote['Date']), lowQuote['Exchange'], lowQuote['Bid Price'], lowQuote['Bid Size'], lowQuote['Ask Price'], lowQuote['Ask Size'], dc.date2rfc(openQuote['Date']), openQuote['Exchange'], openQuote['Bid Price'], openQuote['Bid Size'], openQuote['Ask Price'], openQuote['Ask Size'], dc.date2rfc(closeQuote['Date']), closeQuote['Exchange'], closeQuote['Bid Price'], closeQuote['Bid Size'], closeQuote['Ask Price'], closeQuote['Ask Size']])
        workbook.close()
        del quotes[dateStr]

      dateStr = dc.dateStr(date)
      timeStr = dc.timeStr(date)

    candleQuotes.append({'Date': date, 'Exchange': quote['x'], 'Bid Price': quote['bp'], 'Bid Size': quote['bs'], 'Ask Price': quote['ap'], 'Ask Size': quote['as']})