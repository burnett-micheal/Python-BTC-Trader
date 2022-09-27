class Dataset:
  def __init__(self, maxData):
    self.maxData = maxData
    self.dataset = []
  
  def addData(self, data):
    self.dataset.append(data)
    self.dataset = self.dataset[-self.maxData:]
  
  def len(self):
    return len(self.dataset)
  
  def isMaxLen(self):
    return len(self.dataset) == self.maxData