from bson import json_util
from database import databaseController
import datetime
import time
from threading import Thread
from alarm import alarm
from config import cfg, DATA_PATH, LOG_PATH


CURRENT_DATA = 'currentData'
HISTORY = 'history'
DAILY_HISTORY = 'dailyHistory'
NEXT_UPDATES = 'nextUpdates'

def jsonTimestamp(stringTime, isDate = False):
    if isDate:
        return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d').timetuple())*1000
    else:
        return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S.%f').timetuple())*1000

class WebserverDataUpdater(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		self.dbc = databaseController.databaseController()
		self.alarms = alarm()
		self.lastUpdates = {}

		data = cfg['data']
		databaseName = data['name']

		usedDatabase = data['usedDB']
		db = data[usedDatabase]
		if usedDatabase == 'sqlite':
			self.dbc.enableSqlite(db['path'] + databaseName)
		elif usedDatabase == 'mongo':
			self.dbc.enableMongo(databaseName, db['uri'], DATA_PATH, LOG_PATH)
		else:
			logging.error('Unknown database name')

		offset = cfg['webserver']['updateOffset']

		if cfg['webserver']['liveData']['enable']:
			self.lastUpdates[CURRENT_DATA] = ''
			self.updateCurrentData()

		if cfg['webserver']['charts']['history']['enable']:
			self.lastUpdates[HISTORY] = ''
			self.histoyHeader = []
			for panel in cfg['webserver']['charts']['history']['panels']:
				self.histoyHeader.extend(panel['values'])
			self.updateHistory()

		if cfg['webserver']['charts']['dailyHistory']['enable']:
			self.lastUpdates[DAILY_HISTORY] = ''
			self.dailyHistoyHeader = []
			for panel in cfg['webserver']['charts']['dailyHistory']['panels']:
				for type in panel['values']:
					self.dailyHistoyHeader.extend([type + 'MIN', type + 'MAX', type + 'AVG'])
			self.updateDailyHistory()

		while True:
			toDo = self.alarms.getThingsToDo()
			for func in toDo:
				func()
			time.sleep(5)

	def updateCurrentData(self):
		nextUpdateStr = self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', CURRENT_DATA)
		if self.lastUpdates[CURRENT_DATA] != nextUpdateStr:
			self.lastUpdates[CURRENT_DATA] = nextUpdateStr

			data = { entry['type']: entry['value'] for entry in self.dbc.queryAll(CURRENT_DATA)}

			# check if the file exists, in case it does not exists we create it
			initData = {"data" : data, "nextUpdate" : nextUpdateStr['nextUpdate']}
			with open(DATA_PATH + CURRENT_DATA + '.json', 'w+') as jsonFile:
				jsonFile.write(json_util.dumps(initData))

		offset = cfg['webserver']['updateOffset']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
		self.alarms.addOneTime('updateCurrentData', self.updateCurrentData, nextUpdate + datetime.timedelta(seconds=offset))
		


	def updateHistory(self):
		nextUpdateStr = self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', HISTORY)
		if self.lastUpdates[HISTORY] != nextUpdateStr:
			self.lastUpdates[HISTORY] = nextUpdateStr

			rawData = self.dbc.queryAll(HISTORY)

			# Change representation format and date to timestamp
			data = []
			for rawEntry in rawData:
				entry = []
				for key in self.histoyHeader:
					entry.append(rawEntry[key])
				data.append([rawEntry['date'], entry])

			# check if the file exists, in case it does not exists we create it
			initData = {"data" : data, "nextUpdate" : nextUpdateStr['nextUpdate']}
			with open(DATA_PATH + HISTORY + '.json', 'w+') as jsonFile:
				jsonFile.write(json_util.dumps(initData))

		offset = cfg['webserver']['updateOffset']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
		self.alarms.addOneTime('updateHistory', self.updateHistory, nextUpdate + datetime.timedelta(seconds=offset))


	def updateDailyHistory(self):
		nextUpdateStr = self.dbc.queryOne(['nextUpdate'], NEXT_UPDATES, 'name', DAILY_HISTORY)
		if self.lastUpdates[DAILY_HISTORY] != nextUpdateStr:
			self.lastUpdates[DAILY_HISTORY] = nextUpdateStr

			rawData = self.dbc.queryAll(DAILY_HISTORY)

			# Change representation format and date to timestamp
			data = []
			for rawEntry in rawData:
				entry = []
				for key in self.dailyHistoyHeader:
					entry.append(rawEntry[key])
				data.append([rawEntry['date'], entry])

			# check if the file exists, in case it does not exists we create it
			showAVG = cfg['webserver']['charts']['dailyHistory']['showAVG']
			showMINMAX = cfg['webserver']['charts']['dailyHistory']['showMINMAX']
			initData = {"data" : data, "nextUpdate" : nextUpdateStr['nextUpdate'], "showAVG": showAVG, "showMINMAX": 	showMINMAX}
			with open(DATA_PATH + DAILY_HISTORY + '.json', 'w+') as jsonFile:
				jsonFile.write(json_util.dumps(initData))

		offset = cfg['webserver']['updateOffset']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
		self.alarms.addOneTime('updateDailyHistory', self.updateDailyHistory, nextUpdate + datetime.timedelta(seconds=offset))