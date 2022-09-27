import datetime
from dateutil.relativedelta import relativedelta
import math
import pytz

class Date:
  def date(self, year, month, day, hour, minute, second, microsecond):
    utc = pytz.UTC
    return utc.localize(datetime.datetime(year, month, day, hour, minute, second, microsecond))

  def utcNow(self):
    utc = pytz.UTC
    return utc.localize(datetime.datetime.utcnow())

  def date2rfc(self, date):
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
    utc = pytz.UTC
    return utc.localize(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond)))

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