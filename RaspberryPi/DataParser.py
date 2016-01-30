from bson import json_util
from database import databaseController
from datetime import datetime, timedelta
import time
from threading import Thread
from alarm import alarm
from config import cfg, DATA_PATH, LOG_PATH, IMAGES_FLASK_RELATIVE_PATH


CURRENT_DATA = 'currentData'
HISTORY = 'history'
DAILY_HISTORY = 'dailyHistory'
NEXT_UPDATES = 'nextUpdates'

def str2datetime(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')

def currentTime():
	return datetime.utcnow()

def chooseImage(currentData):
	return IMAGES_FLASK_RELATIVE_PATH + cfg['webserver']['headerImg']

class DataParser():
	def __init__(self):
		self.dbc = databaseController.databaseController()

		data = cfg['data']
		databaseName = data['name']

		usedDatabase = data['usedDB']
		db = data[usedDatabase]
		self.dbc.enableMongo(databaseName, db['uri'], DATA_PATH, LOG_PATH)

		if cfg['webserver']['charts']['history']['enable']:
			self.histoyHeader = []
			for panel in cfg['webserver']['charts']['history']['panels']:
				self.histoyHeader.extend(panel['values'])

		if cfg['webserver']['charts']['dailyHistory']['enable']:
			self.dailyHistoyHeader = []
			for panel in cfg['webserver']['charts']['dailyHistory']['panels']:
				for type in panel['values']:
					self.dailyHistoyHeader.extend([type + 'MIN', type + 'MAX', type + 'AVG'])

	def currentData(self):
		nextUpdate = str2datetime(self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', CURRENT_DATA)['nextUpdate'])

		offset = cfg['webserver']['updateOffset']
		timeToUpdate = (nextUpdate - currentTime()) + timedelta(seconds=offset)

		data = { entry['type']: entry['value'] for entry in self.dbc.queryAll(CURRENT_DATA)}

		jsonData = {"data" : data, "nextUpdate" : timeToUpdate.total_seconds(), "headerImg": chooseImage(data)}

		return jsonData

	def currentDataStr(self):
		return json_util.dumps(self.currentData())
		

	def historyStr(self, sortOrder, limit):
		nextUpdate = str2datetime(self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', HISTORY)['nextUpdate'])

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
		nextUpdate = str2datetime(self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', DAILY_HISTORY)['nextUpdate'])
		
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