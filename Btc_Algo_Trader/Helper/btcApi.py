import requests
import json
from websocket import create_connection
from Helper.date import Date

class BtcApi:
  def __init__(self, ALPACA_API_KEY, ALPACA_SECRET_KEY, TRADE_URL, WEBSOCKET_URL, HISTORY_URL, allowedExchange):
      self.ALPACA_API_KEY = ALPACA_API_KEY
      self.ALPACA_SECRET_KEY = ALPACA_SECRET_KEY
      self.TRADE_URL = TRADE_URL
      self.WEBSOCKET_URL = WEBSOCKET_URL
      self.HISTORY_URL = HISTORY_URL
      self.allowedExchange = allowedExchange

  def btc(self):
    r = requests.get(
      self.TRADE_URL+"/v2/positions/BTCUSD", 
      headers={"APCA-API-KEY-ID":self.ALPACA_API_KEY,"APCA-API-SECRET-KEY":self.ALPACA_SECRET_KEY}, 
    )
    json = r.json()
    if('qty' in json): 
      return float(json['qty'])
    else: 
      return 0

  def cash(self):
    r = requests.get(
      self.TRADE_URL+"/v2/account",
      headers={"APCA-API-KEY-ID":self.ALPACA_API_KEY,"APCA-API-SECRET-KEY":self.ALPACA_SECRET_KEY}
    )
    return float(r.json()['cash'])

  def websocket(self):
    # ws = btcWebsocket()
    # while(1 == 1):
    #   try:
    #     print(ws.recv())
    #   except:
    #     ws = btcWebsocket()   

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
      "key": self.ALPACA_API_KEY, 
      "secret": self.ALPACA_SECRET_KEY
    }

    subCall = {
      "action": "subscribe",
      "quotes": ["BTCUSD"],
    }
    
    ws = create_connection(self.WEBSOCKET_URL)
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
    buyBtcBody = {
      "symbol":"BTCUSD",
      "notional":str(cashAmount),
      "side":"buy",
      "type":"market",
      "time_in_force":"gtc",
    }

    r = requests.post(
      self.TRADE_URL+"/v2/orders", 
      headers={"APCA-API-KEY-ID":self.ALPACA_API_KEY,"APCA-API-SECRET-KEY":self.ALPACA_SECRET_KEY}, 
      data = json.dumps(buyBtcBody)
    )
    
    return r

  def sell(self, btcAmount):  
    sellBtcBody = {
      "symbol":"BTCUSD",
      "qty":str(btcAmount),
      "side":"sell",
      "type":"market",
      "time_in_force":"gtc",
    }

    r = requests.post(
      self.TRADE_URL+"/v2/orders", 
      headers={"APCA-API-KEY-ID":self.ALPACA_API_KEY,"APCA-API-SECRET-KEY":self.ALPACA_SECRET_KEY}, 
      data = json.dumps(sellBtcBody)
    )

    return r
  
  def btcHistory(self, startDate, endDate=None, quoteLimit=None, nextPageToken=None):
    dc = Date()
    reqUrl = self.HISTORY_URL+"/v1beta1/crypto/BTCUSD/quotes?start=" + dc.date2rfc(startDate)
    if(endDate is not None): reqUrl += "&end=" + dc.date2rfc(endDate)
    if(quoteLimit is not None): reqUrl += "&limit=" + str(quoteLimit)
    if(nextPageToken is not None): reqUrl += "&page_token=" + nextPageToken
    if(self.allowedExchange is not None): reqUrl += "&exchanges=" + self.allowedExchange
    reqHeaders = {"APCA-API-KEY-ID":self.ALPACA_API_KEY,"APCA-API-SECRET-KEY":self.ALPACA_SECRET_KEY}
    r = requests.get(reqUrl, headers=reqHeaders)
    if(r.status_code != 200 and r.status_code != 404):
      print(reqUrl)
      print(r)
      raise Exception("Bad Response Code")
    return r.json()