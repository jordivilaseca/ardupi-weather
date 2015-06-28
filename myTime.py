from datetime import datetime
from datetime import timedelta
from datetime import time

class myTime:

	def getCurrentDate():
		return datetime.now().date()

	def getCurrentTime():
		return datetime.now()

	def __init__(self, h=0, m=0, s=0):
		if h == 0 and m == 0 and s == 0:
			self.updates = False
		else:
			self.updateTime = timedelta(hours = h, minutes = m, seconds = s)
			self.lastUpdateDate = myTime.getCurrentDate()
			self.nextUpdateTime = myTime.getCurrentTime()
			self.update()
			self.updates = True

	def setTimeUpdates(self, h, m, s):
		self.__init__(h, m, s)

	def update(self):
		self.nextUpdateTime += self.updateTime

	def isUpdateTime(self):
		return self.nextUpdateTime <= myTime.getCurrentTime()

	def isDifferentDay(self):
		currDate = myTime.getCurrentDate()
		v = self.lastUpdateDate != currDate
		if not v:
			self.lastUpdateDate = currDate
		return v
		