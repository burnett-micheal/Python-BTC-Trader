import math

class CashMaths:
  def __init__(self, maxFloatPoint) -> None:
    self.maxFloatPoint = maxFloatPoint

  def floatFix(self, a):
    mfp = self.maxFloatPoint
    if(a % 1 != 0):
      up = math.ceil(a)
      down = math.floor(a)
      upDiff = up - a
      downDiff = a - down
      if(upDiff <= mfp):
        a = up
      if(downDiff <= mfp):
        a = down
    return a

  def addCash(self, a, b):
    aIsInt = a % 1 == 0
    bIsInt = b % 1 == 0
    if(aIsInt is True and bIsInt is True):
      return a + b
    else:
      xA100 = self.floatFix(a * 100)
      xA100 = xA100 if xA100 % 1 == 0 else math.floor(xA100)
      xB100 = self.floatFix(b * 100)
      xB100 = xB100 if xB100 % 1 == 0 else math.floor(xB100)
      xTotal100 = self.floatFix(xA100 + xB100)
      if(xTotal100 % 1 == 0):
        return xTotal100 / 100
      else:
        return math.floor(xTotal100) / 100

  def subCash(self, a, b):
    aIsInt = a % 1 == 0
    bIsInt = b % 1 == 0
    if(aIsInt is True and bIsInt is True):
      return a - b
    else:
      xA100 = self.floatFix(a * 100)
      xA100 = xA100 if xA100 % 1 == 0 else math.floor(xA100)
      xB100 = self.floatFix(b * 100)
      xB100 = xB100 if xB100 % 1 == 0 else math.floor(xB100)
      xTotal100 = self.floatFix(xA100 - xB100)
      if(xTotal100 % 1 == 0):
        return xTotal100 / 100
      else:
        return math.floor(xTotal100) / 100