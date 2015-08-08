from datetime import datetime
from datetime import timedelta
from datetime import time
import time

def getCurrentDate():
	return datetime.now().date()

def getCurrentTime():
	return datetime.now()

class alarm:

	def __init__(self):
		self.nextUpdates = []
		self.updateTimes = []
		self.functions = []

	def add(self, func, d, h, m, s):
		self.functions.append(func)
		self.nextUpdates.append(getCurrentTime())
		self.updateTimes.append(timedelta(days = d, hours = h, minutes = m, seconds = s))
		self.update(len(self.nextUpdates)-1)

	def addDaily(self, func):
		self.functions.append(func)
		self.nextUpdates.append(datetime.combine(getCurrentDate() + timedelta(days=1), datetime.min.time()))
		self.updateTimes.append(timedelta(days = 1))

	def update(self, pos):
		self.nextUpdates[pos] += self.updateTimes[pos]

	def isUpdateTime(self,pos):
		return self.nextUpdates[pos] <= getCurrentTime()

	def getThingsToDo(self):
		funcs = []
		for i in range(len(self.nextUpdates)):
			if self.isUpdateTime(i):
				funcs.append(self.functions[i])
				self.update(i)
		return funcs
		