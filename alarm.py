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

	def add(self, id, d, h, m, s):
			self.nextUpdates[id] = getCurrentTime()
			self.updateTimes[id] = timedelta(days = d, hours = h, minutes = m, seconds = s)
			self.update([id])

	def update(self, ids):
		for id in ids:
			self.nextUpdates[id] += self.updateTimes[id]

	def isUpdateTime(self,id):
		return self.nextUpdates[id] <= getCurrentTime()

	def getThingsToDo(self):
		return list(filter(self.isUpdateTime, self.nextUpdates.keys()))
		