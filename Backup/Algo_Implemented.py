import datetime
import math
from time import sleep
import pytz
import math
import requests
import json
import os
from websocket import create_connection
from dateutil.relativedelta import relativedelta
from pandas import read_excel
import plotly.graph_objects as go

# TODO: Write Each Trade In BtHistory To File At The End Of BackTest Function
# TODO: Review Backtest For Validity, Update Til You Reach Minimum APY
# TODO: Initiate Quote Handler With Historical Data For X Duration Before Present

# region Global Variables

# Set Now:
#   Real Trading:   https://api.alpaca.markets
#   Paper Trading:  https://paper-api.alpaca.markets
TRADE_URL = "https://paper-api.alpaca.markets"
WEBSOCKET_URL = "wss://stream.data.alpaca.markets"  
ALPACA_API_KEY = "PKW5P6SMLRBVQLK6DYQ3"
ALPACA_SECRET_KEY = "7KzMngilx8lrbRrCEbWrW4dcK660AOdzHZOWIa9J"
allowedExchange = "CBSE"
isBacktest = True
showChart = True

# Set In Runtime:
backtestStart = None
backtestEnd = None
uniqueId = None
tradeHandler = None

#endregion

# region Classes

class _UniqueId:
  _uniqueId = 1
  def get(self):
    idCopy = self._uniqueId
    self._uniqueId += 1
    return idCopy
uniqueId = _UniqueId()

class Date:
  def date(self, year, month, day, hour, minute, second, microsecond):
    return datetime.datetime(year, month, day, hour, minute, second, microsecond)

  def utcNow(self):
    return datetime.datetime.now().astimezone(pytz.UTC)

  def rfc(self, date):
    millisecond = math.floor(date.microsecond/1000)
    def x(num): return num if num >= 10 else "0"+str(num)
    def y(num): 
      if(num >= 100): return num
      if(num >= 10): return "0"+str(num)
      return "00"+str(num)
    date = f'{date.year}-{x(date.month)}-{x(date.day)}T{x(date.hour)}:{x(date.minute)}:{x(date.second)}.{y(millisecond)}Z'
    return date
  
  def rfc2date(self, rfcString):
    year = rfcString.split('-')[0]
    month = rfcString.split('-')[1]
    day = rfcString.split('-')[2].split('T')[0]
    hour = rfcString.split('-')[2].split('T')[1].split(':')[0]
    minute = rfcString.split('-')[2].split('T')[1].split(':')[1]
    second = rfcString.split('-')[2].split('T')[1].split(':')[2]
    microsecond = second.split('.')[1].split('Z')[0][:6] if '.' in second else '0'
    second = second.split('.')[0] if '.' in second else second.split('Z')[0]
    while(len(microsecond) < 6): microsecond += '0'
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond))

  def setYear(self, date, newYear): return datetime.datetime(newYear, date.month, date.day, date.hour, date.minute, date.second, date.microsecond)
  def addYears(self, date, addYear): return date + relativedelta(years = addYear)
  def subYears(self, date, subYear): return date - relativedelta(years = subYear)

  def setMonth(self, date, newMonth): return datetime.datetime(date.year, newMonth, date.day, date.hour, date.minute, date.second, date.microsecond)
  def addMonths(self, date, addMonth): return date + relativedelta(months = addMonth)
  def subMonths(self, date, subMonth): return date - relativedelta(months = subMonth)

  def setDay(self, date, newDay): return datetime.datetime(date.year, date.month, newDay, date.hour, date.minute, date.second, date.microsecond)
  def addDays(self, date, addDay): return date + datetime.timedelta(days = addDay)
  def subDays(self, date, subDay): return date - datetime.timedelta(days = subDay)

  def setHour(self, date, newHour): return datetime.datetime(date.year, date.month, date.day, newHour, date.minute, date.second, date.microsecond)
  def addHours(self, date, addHour): return date + datetime.timedelta(hours = addHour)
  def subHours(self, date, subHour): return date - datetime.timedelta(hours = subHour)

  def setMinute(self, date, newMinute): return datetime.datetime(date.year, date.month, date.day, date.hour, newMinute, date.second, date.microsecond)
  def addMinutes(self, date, addMinute): return date + datetime.timedelta(minutes = addMinute)
  def subMinutes(self, date, subMinute): return date - datetime.timedelta(minutes = subMinute)

  def setSecond(self, date, newSecond): return datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, newSecond, date.microsecond)
  def addSeconds(self, date, addSecond): return date + datetime.timedelta(seconds = addSecond)
  def subSeconds(self, date, subSecond): return date - datetime.timedelta(seconds = subSecond)

  def setMs(self, date, newMs): return datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second, newMs)
  def addMicroseconds(self, date, addMs): return date + datetime.timedelta(microseconds = addMs)
  def subMicroseconds(self, date, subMs): return date - datetime.timedelta(microseconds = subMs)

class FloatingPoint: 
  _maxFloatPoint = 0.000000002
  def intFix(self, a):
    if(a % 1 != 0):
      up = math.ceil(a)
      down = math.floor(a)
      upDiff = up - a
      downDiff = a - down
      if(upDiff <= self._maxFloatPoint):
        a = up
      if(downDiff <= self._maxFloatPoint):
        a = down
    return a

class CashMath:
  def add(self, a, b):
    aIsInt = a % 1 == 0
    bIsInt = b % 1 == 0
    if(aIsInt is True and bIsInt is True):
      return a + b
    else:
      fp = FloatingPoint()
      xA100 = fp.intFix(a * 100)
      xA100 = xA100 if xA100 % 1 == 0 else math.floor(xA100)
      xB100 = fp.intFix(b * 100)
      xB100 = xB100 if xB100 % 1 == 0 else math.floor(xB100)
      xTotal100 = fp.intFix(xA100 + xB100)
      if(xTotal100 % 1 == 0):
        return xTotal100 / 100
      else:
        return math.floor(xTotal100) / 100

  def sub(self, a, b):
    aIsInt = a % 1 == 0
    bIsInt = b % 1 == 0
    if(aIsInt is True and bIsInt is True):
      return a - b
    else:
      fp = FloatingPoint()
      xA100 = fp.intFix(a * 100)
      xA100 = xA100 if xA100 % 1 == 0 else math.floor(xA100)
      xB100 = fp.intFix(b * 100)
      xB100 = xB100 if xB100 % 1 == 0 else math.floor(xB100)
      xTotal100 = fp.intFix(xA100 - xB100)
      if(xTotal100 % 1 == 0):
        return xTotal100 / 100
      else:
        return math.floor(xTotal100) / 100
  
  def mult(self, cash, multiplier):
    fp = FloatingPoint()
    x100 = fp.intFix(cash * multiplier * 100)
    return x100 / 100

  def interest(self, oldPrice, newPrice):
    mod = -1 if oldPrice > newPrice else 1
    percentChange = mod * (abs(newPrice - oldPrice) / oldPrice)
    percentChange = math.floor(percentChange * 1000000)/1000000
    return percentChange

class BtcApi:
  def btc(self):
    global ALPACA_API_KEY
    global ALPACA_SECRET_KEY
    global TRADE_URL
    r = requests.get(
      TRADE_URL+"/v2/positions/BTCUSD", 
      headers={"APCA-API-KEY-ID":ALPACA_API_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET_KEY}, 
    )
    json = r.json()
    if('qty' in json): 
      return float(json['qty'])
    else: 
      return 0

  def cash(self):
    global ALPACA_API_KEY
    global ALPACA_SECRET_KEY
    global TRADE_URL   
    r = requests.get(
      TRADE_URL+"/v2/account",
      headers={"APCA-API-KEY-ID":ALPACA_API_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET_KEY}
    )
    return float(r.json()['cash'])

  def websocket(self):
    # ws = btcWebsocket()
    # while(1 == 1):
    #   try:
    #     print(ws.recv())
    #   except:
    #     ws = btcWebsocket()
    global ALPACA_API_KEY
    global ALPACA_SECRET_KEY
    global WEBSOCKET_URL    

    msg2code = {
    '[{"T":"success","msg":"connected"}]':"0",
    '[{"T":"success","msg":"authenticated"}]':"1",
    '[{"T":"error","code":406,"msg":"connection limit exceeded"}]':"2",
    '[{"T":"error","code":404,"msg":"auth timeout"}]':"3",
    }

    code2msg = {
      "0":"Connected",
      "1":"Authenticated",
      "2":"Connection Limit Exceeded",
      "3":"Authorization Timeout",
    }

    authCall = {
      "action": "auth", 
      "key": ALPACA_API_KEY, 
      "secret": ALPACA_SECRET_KEY
    }

    subCall = {
      "action": "subscribe",
      "trades": ["BTCUSD"],
    }
    
    ws = create_connection(WEBSOCKET_URL+"/v1beta1/crypto")
    recieved = ws.recv()
    ws.send(json.dumps(authCall))
    recieved = ws.recv()
    if(code2msg[msg2code[recieved]] != "Authenticated"): 
      print(recieved)
      raise Exception("Failed To Authenticate Websocket Connection")
    ws.send(json.dumps(subCall))
    recieved = ws.recv()
    return ws

  def buy(self, cashAmount):
    global ALPACA_API_KEY
    global ALPACA_SECRET_KEY
    global TRADE_URL  
    buyBtcBody = {
      "symbol":"BTCUSD",
      "notional":str(cashAmount),
      "side":"buy",
      "type":"market",
      "time_in_force":"gtc",
    }

    r = requests.post(
      TRADE_URL+"/v2/orders", 
      headers={"APCA-API-KEY-ID":ALPACA_API_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET_KEY}, 
      data = json.dumps(buyBtcBody)
    )
    
    return r

  def sell(self, btcAmount):
    global ALPACA_API_KEY
    global ALPACA_SECRET_KEY
    global TRADE_URL    
    sellBtcBody = {
      "symbol":"BTCUSD",
      "qty":str(btcAmount),
      "side":"sell",
      "type":"market",
      "time_in_force":"gtc",
    }

    r = requests.post(
      TRADE_URL+"/v2/orders", 
      headers={"APCA-API-KEY-ID":ALPACA_API_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET_KEY}, 
      data = json.dumps(sellBtcBody)
    )

    return r

class TradeHandler:
  _btCash = 1000
  _api = BtcApi()
  _ownedBtc = _api.btc()
  _minBtcPurchase = 0.0001
  _minBtcIncrement = 0.0001
  _spreadMarkup = 0.001

  # Quote Handler Needs To Access btHistory and holdings
  btHistory = [] # [ {type, date, amount, btcPrice, totalPrice, capital} ]
  holdings = {} # id: {qty, ap}

  def newHolding(self, qty, askingPrice):
    global uniqueId
    id = uniqueId.get()
    if(id in self.holdings): raise Exception("Id Already Exists In Holdings")
    self.holdings[id] = {'qty': qty, 'ap': askingPrice}

  def delHolding(self, id):
    if(id in self.holdings):
      del self.holdings[id]
    else:
      return False
    return True

  def newBtHistory(self, type, date, qty, price, totalPrice):
    dict = {'type': type, 'date': date, 'qty': qty, 'price': price, 'capital': self._btCash}
    dict['totalPrice'] = totalPrice
    self.btHistory.append(dict)

  def btBuy(self, cashRatio, askingPrice, date):
    sAskingPrice = askingPrice * (1 + self._spreadMarkup)
    cash = math.floor(self._btCash * cashRatio * 100) / 100
    btcPurchaseAmount = math.floor((cash / sAskingPrice) / self._minBtcIncrement) * self._minBtcIncrement
    totalLoss = math.ceil(btcPurchaseAmount * sAskingPrice * 100) / 100

    if(btcPurchaseAmount > self._minBtcPurchase):
      cm = CashMath()
      self._btCash = cm.sub(self._btCash, totalLoss)
      self.newBtHistory("buy", date, btcPurchaseAmount, askingPrice, -totalLoss)
      self.newHolding(btcPurchaseAmount, askingPrice)
      return True
    else:
      return False

  def btSell(self, holdingId, biddingPrice, date):
    if(holdingId in self.holdings):
      h = self.holdings[holdingId]
      sBiddingPrice = biddingPrice * (1 - self._spreadMarkup)
      totalGain = math.floor(h['qty'] * sBiddingPrice * 100) / 100
      cm = CashMath()
      self._btCash = cm.add(self._btCash, totalGain)
      self.newBtHistory('sell', date, h['qty'], biddingPrice, totalGain)
      self.delHolding(holdingId)
      return True
    else:
      return False

  def buy(self, askingPrice, cashRatio):
    api = self._api
    liquid = api.cash()
    sAskingPrice = askingPrice * (1 + self._spreadMarkup)
    cash = math.floor(liquid * cashRatio * 100) / 100
    btcPurchaseAmount = math.floor((cash / sAskingPrice) / self._minBtcIncrement) * self._minBtcIncrement
    totalLoss = math.ceil(btcPurchaseAmount * sAskingPrice * 100) / 100

    if(btcPurchaseAmount > self._minBtcPurchase):
      prevBtcOwned = self._ownedBtc
      print("Buy: ", api.buy(totalLoss))
      sleep(5)
      newBtcOwned = api.btc()
      fp = FloatingPoint()
      btcPurchased = fp.intFix(newBtcOwned - prevBtcOwned)
      if(btcPurchased > 0): 
        self.newHolding(btcPurchased, askingPrice)
        return True
      else:
        return False
    else:
      return False

  def sell(self, holdingId):
    api = self._api
    if(holdingId in self.holdings):
      h = self.holdings[holdingId]
      prevCash = api.cash()
      print("Sell: ", api.sell(h['qty']))
      sleep(5)
      newCash = api.cash()
      if(newCash > prevCash):
        self.delHolding(holdingId)
        return True
      else:
        return False
    else:
      return False
tradeHandler = TradeHandler()

class QuoteHandler:
  _candleEnd = None
  _candleQuotes = []
  _candles = []
  _pullbacks = []
  _pullback = {'trend': None, 'start': None, 'mid': None, 'end': None}
  _data = {} # {ss: {'ma': {'b': [] 's':[]}, 'sd': {'b': [] 's':[]}, 't':[]}} - b=buy s=sell ma=moving avg sd=standard deviation t=dates ss=sample size
  _btData = {'b':{'p':[], 't':[]},'s':{'p':[], 't':[]}}
  
  _sdbHighDb = False
  _sdsLowUb= False

  _prevAskPrice = None
  _prevBidPrice = None

  def newQuote(self, quote):
    global allowedExchange
    if(quote['x'] != allowedExchange): return
    global showChart
    global backtestEnd
    global isBacktest
    global tradeHandler
    minInterest = 0.002
    cm = CashMath()
    dc = Date()
    
    # quote = {t, x, bp, bs, ap, as}
    date = quote['t']
    exchange = quote['x']
    bidPrice = quote['bp']
    bidSize = quote['bs']
    askPrice = quote['ap']
    askSize = quote['as']

    isNewCandle = False
    # region Pullback Detection
    if(self._candleEnd is None): self._candleEnd = dc.date(date.year, date.month, date.day, date.hour, date.minute, 59, 999999)

    if(date > self._candleEnd):
      isNewCandle = True
      # Add Candle To Candles
      def addCandle(highQuote, lowQuote, openQuote, closeQuote):
        self._candles.append({'hq': highQuote, 'lq': lowQuote, 'oq': openQuote, 'cq': closeQuote})
      
      if(len(self._candleQuotes) == 1): 
        addCandle(self._candleQuotes[0], self._candleQuotes[0], self._candleQuotes[0], self._candleQuotes[0])
      elif(len(self._candleQuotes) >= 2): 
        oq = self._candleQuotes[0]
        cq = self._candleQuotes[1]
        hq = self._candleQuotes[0]
        lq = self._candleQuotes[1]
        for q in self._candleQuotes:
          if(q['bp'] > hq['bp']): hq = q
          if(q['bp'] < lq['bp']): lq = q
          if(q['t'] < oq['t']):   oq = q
          if(q['t'] > cq['t']):   cq = q
        addCandle(hq, lq, oq, cq)
      
      # Set New Candle Values
      self._candleQuotes = []
      self._candleEnd = dc.date(date.year, date.month, date.day, date.hour, date.minute, 59, 999999)

      # Detect Pullback
      newCandle = self._candles[-1]
      pbKey = None
      if(self._pullback['start'] is None): 
        pbKey = 'start'
      elif(self._pullback['mid'] is None): 
        if(newCandle['hq']['bp'] >= self._pullback['start']['bp']):
          pbKey='start'
        elif(newCandle['hq']['bp'] < self._pullback['start']['bp']):
          pbKey='mid'
      elif(self._pullback['end'] is None): 
        if(newCandle['lq']['bp'] < self._pullback['mid']['bp']):
          pbKey='mid'
        elif(newCandle['lq']['bp'] > self._pullback['mid']['bp']):
          pbKey='end'

      noStart = True if self._pullback['start'] is None else False
      noMid = True if self._pullback['mid'] is None else False
      noEnd = True if self._pullback['end'] is None else False
      tempMid = True if self._pullback['mid'] is None else abs(cm.interest(self._pullback['start']['bp'], self._pullback['mid']['bp'])) < minInterest
      tempEnd = True if self._pullback['end'] is None else abs(cm.interest(self._pullback['mid']['bp'], self._pullback['end']['bp'])) < minInterest

      if(noStart): pbKey = 'start'
      elif(noMid): pbKey = 'mid' if newCandle['hq']['bp'] < self._pullback['start']['bp'] else 'start'
      elif(noEnd): pbKey = 'end' if newCandle['lq']['bp'] > self._pullback['mid']['bp'] else 'mid'

      if(not noEnd): 
        if(newCandle['hq']['bp'] > self._pullback['end']['bp']): pbKey = 'end'
        elif(newCandle['lq']['bp'] < self._pullback['mid']['bp'] or cm.interest(self._pullback['end']['bp'], newCandle['lq']['bp']) < -minInterest): pbKey = 'mid'
      elif(not noMid): pbKey = 'mid' if newCandle['lq']['bp'] < self._pullback['mid']['bp'] else 'start' if tempMid and newCandle['hq']['bp'] > self._pullback['start']['bp'] else 'end'
      elif(not noStart): pbKey = 'start' if newCandle['hq']['bp'] > self._pullback['start']['bp'] else 'mid'

      def addPullback(trend, st, se, sbp, sbs, sap, sas, mt, me, mbp, mbs, map, mas, et, ee, ebp, ebs, eap, eas):
        dict = {
          'trend': trend,
          'start': {
            't': st,
            'x': se,
            'bp':sbp,
            'bs':sbs,
            'ap':sap,
            'as':sas
          },
          'mid': {
            't': mt,
            'x': me,
            'bp':mbp,
            'bs':mbs,
            'ap':map,
            'as':mas
          },
          'end': {
            't': et,
            'x': ee,
            'bp':ebp,
            'bs':ebs,
            'ap':eap,
            'as':eas
          }
        }
        self._pullbacks.append(dict)

      if(pbKey is not None):
        if(pbKey == 'start'): 
          if(tempMid is True or tempEnd is True):
            self._pullback['start'] = newCandle['hq']
            self._pullback['mid'] = None
            self._pullback['end'] = None
            self._pullback['trend'] = None
          else:
            self._pullback['trend'] = 'down' if self._pullback['start']['bp'] > self._pullback['end']['bp'] else 'up'
            pb = self._pullback
            s = pb['start']
            m = pb['mid']
            e = pb['end']
            addPullback(pb['trend'], s['t'], s['x'], s['bp'], s['bs'], s['ap'], s['as'], m['t'], m['x'], m['bp'], m['bs'], m['ap'], m['as'], e['t'], e['x'], e['bp'], e['bs'], e['ap'], e['as'])
            self._pullback['trend'] = None
            self._pullback['start'] = None
            self._pullback['mid'] = None
            self._pullback['end'] = None
        elif(pbKey == 'mid'): 
          if(tempEnd is True):
            self._pullback['mid'] = newCandle['lq']
            self._pullback['end'] = None
          else:
            self._pullback['trend'] = 'down' if self._pullback['start']['bp'] > self._pullback['end']['bp'] else 'up'
            pb = self._pullback
            s = pb['start']
            m = pb['mid']
            e = pb['end']
            addPullback(pb['trend'], s['t'], s['x'], s['bp'], s['bs'], s['ap'], s['as'], m['t'], m['x'], m['bp'], m['bs'], m['ap'], m['as'], e['t'], e['x'], e['bp'], e['bs'], e['ap'], e['as'])
            self._pullback['trend'] = None
            self._pullback['start'] = self._pullback['end']
            self._pullback['mid'] = newCandle['lq']
            self._pullback['end'] = None
        elif(pbKey == 'end'): 
          self._pullback['end'] = newCandle['hq']

    self._candleQuotes.append(quote)

    # endregion
    
    maLowRange = 45
    maHighRange = 120
    if(maHighRange <= maLowRange): Exception("maHighRange is not greater than maLowRange")
    # region Data Collection - Standard Deviation and Moving Average
    maRanges = [maLowRange, maHighRange]
    for ss in maRanges:
      # ss = sample size
      if(len(self._candles) >= ss and isNewCandle == True):
        buyingPrices = []
        sellingPrices = []
        for i in range(ss):
          buyingPrices.append(self._candles[-i+1]['lq']['ap'])
          sellingPrices.append(self._candles[-i+1]['hq']['bp'])
        buyingMean = sum(buyingPrices)/ss
        sellingMean = sum(sellingPrices)/ss
        buyingDeviation = []
        sellingDeviation = []
        for i in range(ss):
          buyingDeviation.append(pow(buyingPrices[i] - buyingMean, 2))
          sellingDeviation.append(pow(sellingPrices[i]-sellingMean, 2))
        sdBuying = math.sqrt(sum(buyingDeviation) / (len(buyingDeviation) - 1))
        sdSelling = math.sqrt(sum(sellingDeviation) / (len(sellingDeviation) - 1))

        if(ss not in self._data): self._data[ss] = {'ma': {'b':[], 's':[]}, 'sd': {'b':[], 's':[]}, 't':[]}
        self._data[ss]['ma']['b'].append(buyingMean)
        self._data[ss]['ma']['s'].append(sellingMean)
        self._data[ss]['sd']['b'].append(buyingMean - sdBuying)
        self._data[ss]['sd']['s'].append(sellingMean + sdSelling)
        self._data[ss]['t'].append(date)
    # endregion
    
    # region Determine Trade Action
    if(isNewCandle and maHighRange in self._data and maLowRange in self._data):
      if(len(self._data[maHighRange]['sd']['b']) > 1):
        prevAskPrice = self._prevAskPrice
        prevBidPrice = self._prevBidPrice
        askPrice = askPrice
        prevSdbHigh = self._data[maHighRange]['sd']['b'][-2]
        sdbHigh = self._data[maHighRange]['sd']['b'][-1]
        prevSdbLow = self._data[maLowRange]['sd']['b'][-2]
        sdbLow = self._data[maLowRange]['sd']['b'][-1]
        prevSdsLow = self._data[maLowRange]['sd']['s'][-2]
        sdsLow = self._data[maLowRange]['sd']['s'][-1]
        sdbHighDb = prevAskPrice > prevSdbHigh and askPrice < sdbHigh
        sdbLowDb = prevAskPrice > prevSdbLow and askPrice < sdbLow
        sdbHighUb = prevAskPrice < prevSdbHigh and askPrice > sdbHigh
        sdsLowUb = prevBidPrice < prevSdsLow and bidPrice > sdsLow
        sdsLowDb = prevBidPrice > prevSdsLow and bidPrice < sdsLow
        if(sdbHighDb and self._sdbHighDb is False):
          self._sdbHighDb = True
        if(self._sdbHighDb):
          if(sdbLowDb):
            self._sdbHighDb = False
            if(isBacktest):
              holdingIds = [holdingId for holdingId in tradeHandler.holdings]
              for holdingId in holdingIds: tradeHandler.btSell(holdingId, bidPrice, date)
              self._btData['s']['p'].append(bidPrice)
              self._btData['s']['t'].append(date)
            else:
              holdingIds = [holdingId for holdingId in tradeHandler.holdings]
              for holdingId in holdingIds: tradeHandler.sell(holdingId)
          elif(sdbHighUb):
            self._sdbHighDb = False
            if(isBacktest):
              tradeHandler.btBuy(1, askPrice, date)
              self._btData['b']['p'].append(askPrice)
              self._btData['b']['t'].append(date)
            else:
              tradeHandler.buy(askPrice, 1)
        if(sdsLowUb and self._sdsLowUb is False):
          self._sdsLowUb = True
        if(self._sdsLowUb and sdsLowDb):
          self._sdsLowUb = False
          if(isBacktest):
            holdingIds = [holdingId for holdingId in tradeHandler.holdings]
            for holdingId in holdingIds: tradeHandler.btSell(holdingId, bidPrice, date)
            self._btData['s']['p'].append(bidPrice)
            self._btData['s']['t'].append(date)
          else:
            holdingIds = [holdingId for holdingId in tradeHandler.holdings]
            for holdingId in holdingIds: tradeHandler.sell(holdingId)
        
    # endregion

    # region Chart
    if(showChart and dc.addMinutes(date, 1) >= backtestEnd and isBacktest):
      pbPrices = []
      pbDates = []
      for pb in self._pullbacks:
        pbPrices.append(pb['start']['bp'])
        pbDates.append(pb['start']['t'])
        pbPrices.append(pb['mid']['bp'])
        pbDates.append(pb['mid']['t'])
        pbPrices.append(pb['end']['bp'])
        pbDates.append(pb['end']['t'])
      
      candleDates = [c['cq']['t']  for c in self._candles]
      openPrices = [c['oq']['bp'] for c in self._candles]
      closePrices = [c['cq']['bp'] for c in self._candles]
      lowPrices = [c['lq']['bp'] for c in self._candles]
      highPrices = [c['hq']['bp'] for c in self._candles]
      candlesticks = go.Candlestick(x=candleDates, open=openPrices, close=closePrices, low=lowPrices, high=highPrices, name="Candles")
      openSct = go.Scatter(x=candleDates, y=openPrices, name="open")
      closeSct = go.Scatter(x=candleDates, y=closePrices, name="close")
      lowSct = go.Scatter(x=candleDates, y=lowPrices, name="low")
      highSct = go.Scatter(x=candleDates, y=highPrices, name="high")
      pbSct = go.Scatter(x=pbDates, y=pbPrices, name = "Pullbacks")
      buySct = go.Scatter(x=self._btData['b']['t'], y=self._btData['b']['p'], name = "Buy Points", mode="markers")
      sellSct = go.Scatter(x=self._btData['s']['t'], y=self._btData['s']['p'], name = "Sell Points", mode="markers")
      figDataArr = [candlesticks, openSct, closeSct, lowSct, highSct, pbSct, buySct, sellSct]
      
      b2sDates = []
      b2sPrices = []
      lastSellDate = None
      for sellIndx, _ignoreMe_ in enumerate(self._btData['s']['t']):
        sellPrice = self._btData['s']['p'][sellIndx]
        sellDate = self._btData['s']['t'][sellIndx]
        for buyIndx, _ignoreMe2_ in enumerate(self._btData['b']['t']):
          buyPrice = self._btData['b']['p'][buyIndx]
          buyDate = self._btData['b']['t'][buyIndx]
          if(lastSellDate is not None):
            if(buyDate < sellDate and buyDate > lastSellDate):
              b2sDates.extend([buyDate, sellDate, None])
              b2sPrices.extend([buyPrice, sellPrice, None])
        lastSellDate = sellDate
      figDataArr.append(go.Scatter(x=b2sDates, y=b2sPrices, name = "Buys 2 Sells"))

      for ss in self._data:
        # ss = sample size
        s = self._data[ss]
        maSellingSct = go.Scatter(x=s['t'], y=s['ma']['s'], name="Moving Avg Selling " + str(ss))
        maBuyingSct =  go.Scatter(x=s['t'], y=s['ma']['b'], name="Moving Avg Buying " + str(ss))
        sdSellingSct = go.Scatter(x=s['t'], y=s['sd']['s'], name="Standard Deviation Selling " + str(ss))
        sdBuyingSct =  go.Scatter(x=s['t'], y=s['sd']['b'], name="Standard Deviation Buying " + str(ss))
        figDataArr.extend([maSellingSct, maBuyingSct, sdSellingSct, sdBuyingSct])
      
      fig = go.Figure(data=figDataArr)

      fig.show()
      exit()
    # endregion

    self._prevAskPrice = askPrice
    self._prevBidPrice = bidPrice
    if(dc.addMinutes(date, 1) >= backtestEnd and isBacktest): print(tradeHandler._btCash)
# endregion

# region Functions

def backtest(dateStart, dateEnd):
  global backtestStart
  global backtestEnd
  global allowedExchange
  backtestStart = dateStart
  backtestEnd = dateEnd
  curDate = dateStart
  dc = Date()
  quoteHandler = QuoteHandler()
  while(curDate < dateEnd):
    fileName = curDate.strftime("%m-%d-%Y")+".xlsx"
    filePath = "./Btc_Quotes_v2/"+allowedExchange+"/"+fileName
    if(os.path.isfile(filePath)):
      print(fileName)
      print(tradeHandler._btCash)
      df = read_excel(filePath)
      quotes = {}
        
      for index, rows in df.iterrows():
        quote = {}
        for key, value in rows.items():
          quote['hq'] = {'t': dc.rfc2date(rows['High Quote Date']), 'x': rows['High Quote Exchange'], 'bp': rows['High Quote Bid Price'], 'bs': rows['High Quote Bid Size'], 'ap': rows['High Quote Ask Price'], 'as': rows['High Quote Ask Size']}
          quote['lq'] = {'t': dc.rfc2date(rows['Low Quote Date']), 'x': rows['Low Quote Exchange'], 'bp': rows['Low Quote Bid Price'], 'bs': rows['Low Quote Bid Size'], 'ap': rows['Low Quote Ask Price'], 'as': rows['Low Quote Ask Size']}
          quote['oq'] = {'t': dc.rfc2date(rows['Open Quote Date']), 'x': rows['Open Quote Exchange'], 'bp': rows['Open Quote Bid Price'], 'bs': rows['Open Quote Bid Size'], 'ap': rows['Open Quote Ask Price'], 'as': rows['Open Quote Ask Size']}
          quote['cq'] = {'t': dc.rfc2date(rows['Close Quote Date']), 'x': rows['Close Quote Exchange'], 'bp': rows['Close Quote Bid Price'], 'bs': rows['Close Quote Bid Size'], 'ap': rows['Close Quote Ask Price'], 'as': rows['Close Quote Ask Size']}
        quotes[rows['Time']] = quote

      for _ignoreMe_, quote in quotes.items():
        quoteHandler.newQuote(quote['hq'])
        quoteHandler.newQuote(quote['lq'])
        quoteHandler.newQuote(quote['oq'])
        quoteHandler.newQuote(quote['cq'])

      print(tradeHandler.holdings)
      print(tradeHandler._btCash)
      print(" - - - - - - - - - - - - - - - - - - ")
      
    curDate = dc.addDays(curDate, 1)
    
# endregion

# region Main

dc = Date()

# Up Trend Backtest
backtest(dc.date(2022, 1, 1, 0, 0, 0, 0), dc.date(2022, 1, 2, 0, 0, 0, 0))

# Down Trend Backtest
# backtest(dc.date(2022, 3, 31, 0, 0, 0, 0), dc.date(2022, 4, 1, 0, 0, 0, 0))

# endregion