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
startDate = dc.date(2022, 1, 9, 0, 0, 0, 0)
endDate = dc.date(2022, 4, 3, 0, 0, 0, 0)
nextPageToken = 'None'
quotes = {}
# Exchange: { 03/04/2021: {00:00: {hq, lq, oq, cq}}} 
# quote = { 't': , 'x': , 'ap': , 'as': , 'bp': , 'bs': }
dateStr = None
timeStr = None
candleQuotes = [] # { 't': , 'x': , 'bp': , 'bs': , 'ap': , 'as': } 

while(nextPageToken != None):
  r = None
  if(nextPageToken == 'None'):
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
      xQuotes = {}
      
      for cq in candleQuotes:
        if(cq['x'] not in xQuotes): xQuotes[cq['x']] = []
        xQuotes[cq['x']].append(cq)
      
      for ex in xQuotes:
        hq = None
        lq = None
        oq = None
        cq = None
        for i,q in enumerate(xQuotes[ex]):
          if(ex not in quotes): quotes[ex] = {}
          if(dateStr not in quotes[ex]): quotes[ex][dateStr] = {}
          if(i == 0): hq = lq = oq = cq = q
          if(q['bp'] > hq['bp']): hq = q
          if(q['bp'] < lq['bp']): lq = q
          if(dc.rfc2date(q['t']) < dc.rfc2date(oq['t'])): oq = q
          if(dc.rfc2date(q['t']) > dc.rfc2date(cq['t'])): cq = q
        quotes[ex][dateStr][timeStr] = {'hq': hq, 'lq': lq, 'oq': oq, 'cq': cq}
      
      if(dateStr != dc.dateStr(date)):
        for ex in quotes:
          newDir = './Btc_Quotes_v2/'+ex
          if not os.path.exists(newDir): os.makedirs(newDir)
          for _dateStr in quotes[ex]:
            fileName = _dateStr+'.xlsx'
            workbook = xlsxwriter.Workbook(newDir+"/"+fileName)
            worksheet = workbook.add_worksheet()
            row = 0
            worksheet.write_row(row, 0, ['Time', 'High Quote Date', 'High Quote Exchange', 'High Quote Bid Price', 'High Quote Bid Size', 'High Quote Ask Price', 'High Quote Ask Size', 'Low Quote Date', 'Low Quote Exchange', 'Low Quote Bid Price', 'Low Quote Bid Size', 'Low Quote Ask Price', 'Low Quote Ask Size', 'Open Quote Date', 'Open Quote Exchange', 'Open Quote Bid Price', 'Open Quote Bid Size', 'Open Quote Ask Price', 'Open Quote Ask Size', 'Close Quote Date', 'Close Quote Exchange', 'Close Quote Bid Price', 'Close Quote Bid Size', 'Close Quote Ask Price', 'Close Quote Ask Size'])
            for _timeStr in quotes[ex][_dateStr]:
              row += 1
              candle = quotes[ex][_dateStr][_timeStr]
              hq = candle['hq']
              lq = candle['lq']
              oq = candle['oq']
              cq = candle['cq']
              worksheet.write_row(row, 0, [_timeStr, hq['t'], hq['x'], hq['bp'], hq['bs'], hq['ap'], hq['as'], lq['t'], lq['x'], lq['bp'], lq['bs'], lq['ap'], lq['as'], oq['t'], oq['x'], oq['bp'], oq['bs'], oq['ap'], oq['as'], cq['t'], cq['x'], cq['bp'], cq['bs'], cq['ap'], cq['as']])
            workbook.close()
        quotes = {}

      dateStr = dc.dateStr(date)
      timeStr = dc.timeStr(date)
      candleQuotes = []

    candleQuotes.append(quote)

