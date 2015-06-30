from datetime import datetime
from datetime import timedelta
from datetime import time
import time

class alarm:

	def getCurrentDate():
		return datetime.now().date()

	def getCurrentTime():
		return datetime.now()

	def __init__(self):
		self.nextUpdates = {}
		self.updateTimes = {}

	def add(self, id, d, h, m, s):
			self.nextUpdates[id] = alarm.getCurrentTime()
			self.updateTimes[id] = timedelta(days = d, hours = h, minutes = m, seconds = s)

	def update(self, ids):
		for id in ids:
			self.nextUpdates[id] += self.updateTimes[id]

	def isUpdateTime(self,id):
		return self.nextUpdates[id] <= alarm.getCurrentTime()

	def getElementsToUpdate(self):
		return list(filter(self.isUpdateTime, self.nextUpdates.keys()))
		