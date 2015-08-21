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
		self.nextUpdates = {}
		self.updateTimes = {}
		self.functions = {}

	def add(self, id, func, d, h, m, s):
		self.functions[id] = func
		self.nextUpdates[id] = getCurrentTime()
		self.updateTimes[id] = timedelta(days = d, hours = h, minutes = m, seconds = s)
		self.update(id)

	def addDaily(self, id, func):
		self.functions[id] = func
		self.nextUpdates[id] = datetime.combine(getCurrentDate() + timedelta(days=1), datetime.min.time())
		self.updateTimes[id] = timedelta(days = 1)

	def addOneTime(self, id, func, dateTime):
		self.functions[id] = func
		self.nextUpdates[id] = dateTime
		self.updateTimes[id] = None

	def update(self, id):
		self.nextUpdates[id] += self.updateTimes[id]

	def remove(self, id):
		del self.nextUpdates[id]
		del self.updateTimes[id]
		del self.functions[id]

	def getNextUpdateStr(self, id):
		return self.nextUpdates[id].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

	def isUpdateTime(self,id):
		return self.nextUpdates[id] <= getCurrentTime()

	def getThingsToDo(self):
		funcs = []
		for key in self.nextUpdates.keys():
			if self.isUpdateTime(key):
				funcs.append(self.functions[key])
				if self.updateTimes[key] != None:
					self.update(key)
				else:
					self.remove(key)
		return funcs
		