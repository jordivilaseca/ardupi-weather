from datetime import datetime
from datetime import timedelta
from datetime import time

class myTime:
	def __init__(self, h, m, s):
		self.updateTime = timedelta(hours = h, minutes = m, seconds = s)
		self.lastUpdateDate = myTime.getCurrentDate()
		self.nextUpdateTime = myTime.getCurrentTime()
		self.update()

	def getCurrentDate():
		return datetime.now().date()

	def getCurrentTime():
		return datetime.now()

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
		