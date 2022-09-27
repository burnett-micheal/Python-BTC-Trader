import math
from Helper.btcApi import BtcApi
from Helper.uniqueId import UniqueId
from Helper.cashMaths import CashMaths

class TradeHandler:
  def __init__(self, isBacktest, btCash, btcApi: BtcApi, spreadMarkup, minBtcPurchase, minBtcIncrement, maxFloatPoint):
    self.isBacktest = isBacktest
    self.btCash = btCash
    self.btcApi = btcApi
    self.spreadMarkup = spreadMarkup
    self.minBtcPurchase = minBtcPurchase
    self.minBtcIncrement = minBtcIncrement
    self.holdings = {}
    self.btHistory = []
    self.ownedBtc = btcApi.btc()
    self.uniqueId = UniqueId()
    self.cashMaths = CashMaths(maxFloatPoint)

  def newHolding(self, amount, price):
    id = self.uniqueId.get()
    if(id in self.holdings): raise Exception("Id Already Exists In Holdings")
    self.holdings[id] = {'amount': amount, 'btcPrice': price}

  def delHolding(self, id):
    if(id in self.holdings):
      del self.holdings[id]
    else:
      return False
    return True

  def newBtHistory(self, type, date, amount, price, totalPrice):
    self.btHistory.append({'type': type, 'date': date, 'amount': amount, 'btcPrice': price, 'totalPrice': totalPrice, 'capital': self.btCash})

  def btBuy(self, cashRatio, price, date):
    cash = math.floor(self.btCash * cashRatio * 100) / 100
    invertedInc = 1 / self.minBtcIncrement
    sPrice = price * (1 + self.spreadMarkup)
    btcPurchaseAmount = math.floor((cash / sPrice) * invertedInc) / invertedInc
    cash = math.ceil(btcPurchaseAmount * sPrice * 100) / 100

    if(btcPurchaseAmount > self.minBtcPurchase):
      self.btCash = self.cashMaths.subCash(self.btCash, cash)
      self.newBtHistory("buy", date, btcPurchaseAmount, price, -cash)
      self.newHolding(btcPurchaseAmount, price)
      return True
    else:
      return False

  def btSell(self, holdingId, price, date):
    if(holdingId in self.holdings):
      h = self.holdings[holdingId]
      sPrice = price * (1 - self.spreadMarkup)
      nowValue = math.floor(h['amount'] * sPrice * 100) / 100
      self.btCash = self.cashMaths.addCash(self.btCash, nowValue)
      self.newBtHistory('sell', date, h['amount'], price, nowValue)
      self.delHolding(holdingId)
      return True
    else:
      return False
  
  def btSellAll(self, price, date):
    ids = []
    for id in self.holdings: ids.append(id)
    for id in ids: self.btSell(id, price, date)

  def buy(self, cashRatio, bidPrice):
    liquid = self.btcApi.cash()
    price = bidPrice
    cash = math.floor(liquid * cashRatio * 100) / 100
    invertedInc = 1 / self.minBtcIncrement
    price = price * (1 + self.spreadMarkup)
    btcPurchaseAmount = math.floor((cash / price) * invertedInc) / invertedInc
    cash = math.ceil(btcPurchaseAmount * price * 100) / 100

    if(btcPurchaseAmount > self.minBtcPurchase):
      prevBtcOwned = self.btcApi.btc()
      print("Buy: ", self.btcApi.buy(cash))
      newBtcOwned = self.btcApi.btc()
      btcPurchased = self.cashMaths.floatFix(newBtcOwned - prevBtcOwned)
      if(btcPurchased > 0): 
        self.newHolding(btcPurchased, price)
        return True
      else:
        return False
    else:
      return False

  def sell(self, holdingId):
    if(holdingId in self.holdings):
      h = self.holdings[holdingId]
      prevCash = self.btcApi.cash()
      print("Sell: ", self.btcApi.sell(h['amount']))
      newCash = self.btcApi.cash()
      if(newCash > prevCash):
        self.delHolding(holdingId)
        return True
      else:
        return False
    else:
      return False