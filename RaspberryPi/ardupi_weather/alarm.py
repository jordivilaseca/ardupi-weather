from datetime import datetime
from datetime import timedelta
from datetime import time
import time

def getCurrentDate():

	"""
	Get current utc date.

	Returns:
		A date object containing the current utc date.
	"""

	return datetime.utcnow().date()

def getCurrentTime():

	"""
	Get current utc time.

	Returns:
		A datetime object containing the current utc time.
	"""

	return datetime.utcnow()

class Alarm:

	"""
	Class used for tasks management, you can add a one time alarm for a specific time, or an alarm every
	X time. Using the function getThingsToDo you can know which tasks need to be done, each alarm is assigned
	to a specific function, and when a task is need to be done the specific function is returned.
	"""

	def __init__(self):

		"""
		It initializes the alarm system, the initial state do not have any alarm.
		"""

		self.nextUpdates = {}
		self.updateTimes = {}
		self.functions = {}

	def add(self, id, func, d, h, m, s):

		"""
		It adds an alarm that will be executed every whatever time is configured starting from the moment that
		this function is called.

		Args:
			id: An identifier for the alarm.
			func: Function to be returned when the task needs to be done.
			d: The task will be executed each d days, h hours, m minutes and s seconds.
			h: The task will be executed each d days, h hours, m minutes and s seconds.
			m: The task will be executed each d days, h hours, m minutes and s seconds.
			s: The task will be executed each d days, h hours, m minutes and s seconds.
		"""

		self.functions[id] = func
		self.nextUpdates[id] = getCurrentTime()
		self.updateTimes[id] = timedelta(days = d, hours = h, minutes = m, seconds = s)
		self.update(id)

	def addDaily(self, id, func):

		"""
		It will add a daily alarm, it will be executed every day at midnight.

		Args:
			id: An identifier for the alarm.
			func: Function to be returned when the task needs to be done.
		"""

		self.functions[id] = func
		self.nextUpdates[id] = datetime.combine(getCurrentDate() + timedelta(days=1), datetime.min.time())
		self.updateTimes[id] = timedelta(days = 1)

	def addOneTime(self, id, func, dateTime):

		"""
		It will add a on time alarm, the alarm is automatically removed after the user is warned.

		Args:
			id: An identifier for the alarm.
			func: Function to be returned when the task needs to be done.
			dateTime: A datetime object containing the alarm time.
		"""

		self.functions[id] = func
		self.nextUpdates[id] = dateTime
		self.updateTimes[id] = None

	def update(self, id):

		"""
		It updates the time of a periodic alarm

		Args:
			id: An identifier for the alarm.
		"""

		self.nextUpdates[id] += self.updateTimes[id]

	def remove(self, id):

		"""
		It removes an alarm.

		Args:
			id: An identifier for the alarm.
		"""

		del self.nextUpdates[id]
		del self.updateTimes[id]
		del self.functions[id]

	def getNextUpdateStr(self, id):

		"""
		It returns a string containing for what time the alarm is setted.

		Args:
			id: An identifier for the alarm.

		Returns:
			A string containing the alarm time.
		"""
		return self.nextUpdates[id].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

	def isUpdateTime(self,id):

		"""
		It returns if it is the moment to do a task.

		Args:
			id: An identifier for the alarm.

		Returns:
			A boolean that means if is the moment to do a task or not.
		"""

		return self.nextUpdates[id] <= getCurrentTime()

	def getThingsToDo(self):

		"""
		Get all the tasks that need to be done.

		Returns:
			A list of functions that need to be executed.
		"""

		funcs = []
		for key in self.nextUpdates.keys():
			if self.isUpdateTime(key):
				funcs.append(self.functions[key])
				if self.updateTimes[key] != None:
					self.update(key)
				else:
					self.remove(key)
		return funcs
