from Data.dataset import Dataset
from Helper.misc import interest
import math

class DatasetMaths:
  def getStandardDeviation(self, dataset):
    if(isinstance(dataset, Dataset)):
      dataset = dataset.dataset
      mean = sum(dataset)/len(dataset)
      deviations = []
      for data in dataset: deviations.append(pow(data - mean, 2))
      return math.sqrt(sum(deviations) / (len(deviations) - 1))
    else:
      Exception("dataset Is Not A Dataset Class")

  def getMovingAverage(self, dataset):
    if(isinstance(dataset, Dataset)):
      dataset = dataset.dataset
      movingAvg = sum(dataset)/len(dataset)
      return movingAvg
    else:
      Exception("dataset Is Not A Dataset Class")

  def getExponentialMovingAverage(self, dataset):
    ema = []
    j = 1
    n = dataset.len()
    values = dataset.dataset

    #get n sma first and calculate the next n period ema
    sma = self.getMovingAverage(dataset)
    multiplier = 2 / (n + 1)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (values[-1] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in values:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j += 1
        ema.append(tmp)

    return ema[-1]
  
  def getSmoothedMovingAverage(self, dataset):
    ema = []
    j = 1
    n = dataset.len()
    values = dataset.dataset

    #get n sma first and calculate the next n period ema
    sma = self.getMovingAverage(dataset)
    multiplier = 1/n
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (values[-1] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in values:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j += 1
        ema.append(tmp)

    return ema[-1]
  
  def getTrueRange(self, dataset):
    high = max(dataset.dataset)
    low = min(dataset.dataset)
    close = dataset.dataset[-1]
    hl = high - low
    hc = abs(high - close)
    lc = abs(low - close)
    return max([hl, hc, lc])

  def getPullbacks(self, dataset, minInterest):
    if(isinstance(dataset, Dataset)):
      dataset = dataset.dataset
      pullbacks = []
      
      pbStart = None
      pbMid = None
      pbEnd = None
      pbKey = None
      for data in dataset:
        if(pbStart is None):
          pbKey = 'start'
        elif(pbMid is None):
          if(data >= pbStart):
            pbKey = 'start'
          elif(data < pbStart):
            pbKey = 'mid'
        elif(pbEnd is None):
          if(data < pbMid):
            pbKey = 'mid'
          elif(data > pbMid):
            pbKey = 'end'

        noStart = True if pbStart is None else False
        noMid = True if pbMid is None else False
        noEnd = True if pbEnd is None else False
        tempMid = True if pbMid is None else abs(interest(pbStart, pbMid)) < minInterest
        tempEnd = True if pbEnd is None else abs(interest(pbMid, pbEnd)) < minInterest

        if(noStart): pbKey = 'start'
        elif(noMid): pbKey = 'mid' if data < pbStart else 'start'
        elif(noEnd): pbKey = 'end' if data > pbMid else 'mid'

        if(not noEnd): 
          if(data > pbEnd): pbKey = 'end'
          elif(data < pbMid or interest(pbEnd, data) < -minInterest): pbKey = 'mid'
        elif(not noMid): pbKey = 'mid' if data < pbMid else 'start' if tempMid and data > pbStart else 'end'
        elif(not noStart): pbKey = 'start' if data > pbStart else 'mid'

        if(pbKey is not None):
          if(pbKey == 'start'): 
            if(tempMid is True or tempEnd is True):
              pbStart = data
              pbMid = None
              pbEnd = None
            else:
              pullbacks.append({'start': pbStart, 'mid': pbMid, 'end': pbEnd})
              pbStart = None
              pbMid = None
              pbEnd = None
          elif(pbKey == 'mid'): 
            if(tempEnd is True):
              pbMid = data
              pbEnd = None
            else:
              pullbacks.append({'start': pbStart, 'mid': pbMid, 'end': pbEnd})
              pbStart = pbEnd
              pbMid = data
              pbEnd = None
          elif(pbKey == 'end'): 
            pbEnd = data

      return pullbacks
    else:
      Exception("dataset Is Not A Dataset Class")
  
  def getBBHigh(self, closingDataset):
    return self.getMovingAverage(closingDataset)+(2*self.getStandardDeviation(closingDataset))
  def getBBMid(self, closingDataset):
    return self.getMovingAverage(closingDataset)
  def getBBLow(self, closingDataset):
    return self.getMovingAverage(closingDataset)-(2*self.getStandardDeviation(closingDataset))