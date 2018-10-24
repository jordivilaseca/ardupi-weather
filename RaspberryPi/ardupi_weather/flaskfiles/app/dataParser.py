from bson import json_util
from ardupi_weather.database.databaseController import DatabaseController
from datetime import datetime, timedelta
import time
from ardupi_weather.config import cfg, DATA_PATH, LOG_PATH, IMAGES_FLASK_RELATIVE_PATH


CURRENT_DATA = cfg['data']['currentData']['name']
HISTORY = cfg['data']['history']['name']
DAILY_HISTORY = cfg['data']['dailyHistory']['name']
NEXT_UPDATES = 'nextUpdates'

def str2datetime(s):

	"""
	Function that transforms a string datetime to a datetime object.

	Args:
		s: String datetime.

	Returns:
		A datetime object.
	"""
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')

def currentTime():

	"""
	Function that returns the current datetime.

	Returns:
		Current utc datetime.
	"""
	return datetime.utcnow()

def chooseImage(currentData):

	"""
	Function in charge of returning the image to show as a webpage header.

	Args:
		currentData: Dictionary containing the current data.

	Returns:
		Path to the header file.
	"""
	return IMAGES_FLASK_RELATIVE_PATH + cfg['webserver']['headerImage']

class DataParser():

	"""
	Class in charge of parsing the data stored to the database to json strings.
	"""
	def __init__(self):

		"""
		Initialization of the class.

		The configuration parameters are read from the configuration file.
		"""
		self.dbc = DatabaseController()

		data = cfg['data']
		databaseName = data['name']

		usedDatabase = data['usedDB']
		db = data[usedDatabase]

		if usedDatabase == 'sqlite':
			self.dbc.enableSqlite(db['path'] + databaseName)
		elif usedDatabase == 'mongo':
			self.dbc.enableMongo(databaseName, db['uri'], DATA_PATH, LOG_PATH)
		else:
			'Unknown database name'

		if cfg['webserver']['charts']['history']['enable']:
			self.histoyHeader = []
			for panel in cfg['webserver']['charts']['history']['panels']:
				self.histoyHeader.extend(panel['values'])

		if cfg['webserver']['charts']['dailyHistory']['enable']:
			self.dailyHistoyHeader = []
			for panel in cfg['webserver']['charts']['dailyHistory']['panels']:
				for type in panel['values']:
					self.dailyHistoyHeader.extend([type + 'MIN', type + 'MAX', type + 'AVG'])

	def currentDataStr(self):

		"""
		It reads and returns the current data from the database.

		Returns:
			A json string containing the current data from the database.
		"""

		nextUpdate = str2datetime(self.dbc.queryOne(NEXT_UPDATES, 'name', CURRENT_DATA)['nextUpdate'])

		offset = cfg['webserver']['updateOffset']
		timeToUpdate = (nextUpdate - currentTime()) + timedelta(seconds=offset)

		data = { entry['type']: entry['value'] for entry in self.dbc.queryAll(CURRENT_DATA)}

		jsonData = {"data" : data, "nextUpdate" : timeToUpdate.total_seconds(), "headerImg": chooseImage(data)}

		return json_util.dumps(jsonData)


	def historyStr(self, sortOrder, limit):
		"""
		It reads and returns the history data from the database.

		The data can be stored in ascendant or descendent order, and the number of entries to return limited to
		a number.

		Args:
			sortOrder: 1 is ascending order, -1 is descending order.
			limit: Number of entries to fetch. If it is 0 it will fetch all the entries.

		Returns:
			A json string containing the history data from the database.
		"""

		nextUpdate = str2datetime(self.dbc.queryOne(NEXT_UPDATES, 'name', HISTORY)['nextUpdate'])

		offset = cfg['webserver']['updateOffset']
		timeToUpdate = (nextUpdate - currentTime()) + timedelta(seconds=offset)

		rawData = self.dbc.querySortLimit(HISTORY, 'date', sortOrder, limit)

		# Change representation format and date to timestamp
		data = []
		for rawEntry in rawData:
			entry = []
			for key in self.histoyHeader:
				entry.append(rawEntry[key])
			data.append([rawEntry['date'], entry])

		jsonData = {"data" : data, "nextUpdate" : timeToUpdate.total_seconds()}

		return json_util.dumps(jsonData)


	def dailyHistoryStr(self, sortOrder, limit):

		"""
		It reads and returns the daily history data from the database.

		The data can be stored in ascendant or descendent order, and the number of entries to return limited to
		a number.

		Args:
			sortOrder: 1 is ascending order, -1 is descending order.
			limit: Number of entries to fetch. If it is 0 it will fetch all the entries.

		Returns:
			A json string containing the daily history data from the database.
		"""

		nextUpdate = str2datetime(self.dbc.queryOne(NEXT_UPDATES, 'name', DAILY_HISTORY)['nextUpdate'])

		offset = cfg['webserver']['updateOffset']
		timeToUpdate = (nextUpdate - currentTime()) + timedelta(seconds=offset)

		rawData = self.dbc.querySortLimit(DAILY_HISTORY, 'date', sortOrder, limit)

		# Change representation format and date to timestamp
		data = []
		for rawEntry in rawData:
			entry = []
			for key in self.dailyHistoyHeader:
				entry.append(rawEntry[key])
			data.append([rawEntry['date'], entry])

		showAVG = cfg['webserver']['charts']['dailyHistory']['showAVG']
		showMINMAX = cfg['webserver']['charts']['dailyHistory']['showMINMAX']
		jsonData = {"data" : data, "nextUpdate" : timeToUpdate.total_seconds(), "showAVG": showAVG, "showMINMAX": showMINMAX}

		return json_util.dumps(jsonData)
