#!/usr/bin/python

from config import cfg, dataPath, logPath
from arduino.arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import json

LOG_FILE = logPath + 'station.log'
handler = TimedRotatingFileHandler(LOG_FILE, when="d", interval=7, backupCount=6)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

logger = logging.getLogger('station')
logger.setLevel(logging.INFO)

logger.addHandler(handler)


def getDatetime():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def getDate():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def formatDatetime(date):
	return date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def jsonTimestamp(stringTime, isDate):
	if isDate:
		return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d').timetuple())*1000
	else:
		return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S.%f').timetuple())*1000

def updateJsonFile(jsonFilePath, dataHeader, newValues, nextUpdate, isDate = False):
	# Read data
	with open(jsonFilePath, 'r') as jsonFile:
		data = json.load(jsonFile)

	# Update data dictionary
	newValuesList = [newValues[key] for key in dataHeader]
	data['data'].append([jsonTimestamp(newValues['date'], isDate),newValuesList])

	# set new update time
	data['nextUpdate'] = nextUpdate

	# Update file
	with open(jsonFilePath, 'w') as jsonFile:
		json.dump(data, jsonFile)

def createFile(filePath, initData):
	if not os.path.exists(filePath):
		with open(filePath, 'w+') as jsonFile:
			jsonFile.write(initData)

def printSensor(sensor, value):
	date = getDatetime()
	print (date, sensor, value)

class station:
	def __init__(self):
		self.dbc = databaseController.databaseController()
		self.newValueFunctions = []
		self.alarms = alarm()

		self.sensorData = cfg['arduino']['sensors']
		self.sensorNamesList = list(self.sensorData.keys())

		self.sensorTypes = cfg['data']['values']
		self.sensorUnits = {key: self.sensorTypes[value] for key,value in self.sensorData.items()}		

		#Configure arduino
		arduinoCfg = cfg['arduino']
		self.configureArduino(arduinoCfg)

		#Configure database
		dataCfg = cfg['data']
		self.configureDatabase(dataCfg)

		#Initialize history database
		historyCfg = dataCfg['history']
		self.initialitzeHistoryDatabase(historyCfg)

		#Initialize daily history database
		dailyHistoryCfg = dataCfg['dailyHistory']
		self.initializeDailyHistoryDatabase(dailyHistoryCfg, historyCfg)

		#configure station for webserver support
		webserverCfg = cfg['webserver']
		self.configureWebserverSupport(webserverCfg, historyCfg, dailyHistoryCfg)

		#Initialize terminal input
		self.t = terminal()

	#Configuration functions

	def configureArduino(self, ard):
		connection = ard['usedConnection']
		self.ard = arduino(connection, ard[connection], self.sensorUnits)

	def configureDatabase(self, data):
		self.databaseName = data['name']

		usedDatabase = data['usedDB']
		db = data[usedDatabase]
		if usedDatabase == 'sqlite':
			self.dbc.enableSqlite(db['path'] + self.databaseName)
		elif usedDatabase == 'mongo':
			self.dbc.enableMongo(self.databaseName, db['server'], db['port'])
		else:
			'Unknown database name'

	def initialitzeHistoryDatabase(self, history):
		if history['enable']:
			self.dbHistoryHeader = {'date' : 'TEXT'}
			self.dbHistoryHeader.update(self.sensorTypes)

			self.historyDataName = history['name']
			self.dbc.createDataContainer(self.historyDataName, self.dbHistoryHeader)
			self.sensorSum = dict.fromkeys(self.sensorTypes, 0)
			self.sensorNum = dict.fromkeys(self.sensorTypes, 0)

			update = history['updateEvery']
			self.alarms.add('updateHistory', self.updateHistory, update['d'], update['h'], update['m'], update['s'])

			self.newValueFunctions.append(self.updateHistoryData)

	def initializeDailyHistoryDatabase(self, daily, history):
		if daily['enable']:
			if not history['enable']:
				print ("Daily history cannot be enabled because 'history' is not enabled")
				return

			self.dbDailyHistoryHeader = {'date' : 'TEXT'}
			self.dbDailyHistoryHeader.update({key + 'MAX': value for key,value in self.sensorTypes.items()})
			self.dbDailyHistoryHeader.update({key + 'MIN': value for key,value in self.sensorTypes.items()})
			self.dbDailyHistoryHeader.update({key + 'AVG': value for key,value in self.sensorTypes.items()})

			self.dailyHistoryDBName = daily['name']
			self.dbc.createDataContainer(self.dailyHistoryDBName, self.dbDailyHistoryHeader)

			self.alarms.addDaily('updateDailyHistory', self.updateDailyHistory)

	def initialitzeCurrentData(self, currentData):
		if currentData['enable']:
			self.currentDataFile = currentData['path'] + "currentData.json"

			self.currentDataValues = {}

			update = currentData['updateEvery']
			self.alarms.add('updateCurrentData', self.updateCurrentDataFile, update['d'], update['h'], update['m'], update['s'])

			self.newValueFunctions.append(self.updateCurrentData)

			# check if the file exists, in case it does not exists we create it
			initData = '{ "data" : {}, "nextUpdate" : "' + self.alarms.getNextUpdateStr('updateCurrentData') + '"}'
			createFile(self.currentDataFile, initData)

	def configureWebserverSupport(self, webserver, history, dailyHistory):
		if webserver['enable']:
			if not (history['enable'] and dailyHistory['enable']):
				print("webserver cannot be enabled because 'history' or 'dailyHistory' are not enabled")
				return

			self.configureWebserverCharts(webserver['charts'])
			self.initialitzeCurrentData(webserver['liveData'])

	def configureWebserverCharts(self, charts):

		# Initialize history chart structures
		historyChart = charts['history']
		if historyChart['enable']:
			self.historyJsonFilePath = dataPath + 'history.json'

			# check if the file exists, in case it does not exists we create it
			initData = '{ "data" : [], "nextUpdate" : "' + self.alarms.getNextUpdateStr('updateHistory') + '"}'
			createFile(self.historyJsonFilePath, initData)

			self.historyJsonDataHeader = []
			for panel in historyChart['panels']:
				self.historyJsonDataHeader.extend(list(panel['values']))
			self.historyJson = True
		else:
			self.historyJson = False

		dailyHistoryChart = charts['dailyHistory']
		if dailyHistoryChart['enable']:
			self.dailyHistoryJsonFilePath = dataPath + 'dailyHistory.json'

			# check if the file exists, in case it does not exists we create it
			initData = '{ "data" : [], "nextUpdate" : "' + self.alarms.getNextUpdateStr('updateDailyHistory') + '"}'
			createFile(self.dailyHistoryJsonFilePath,initData)

			self.dailyHistoryJsonDataHeader = []
			for data in self.historyJsonDataHeader:
				self.dailyHistoryJsonDataHeader.extend([data + 'MIN', data + 'MAX', data + 'AVG'])
			self.dailyHistoryJson = True
		else:
			self.dailyHistoryJson = False

	#Functions to execute when a new sensor value arrives
	def updateCurrentData(self, valueType, value):
		self.currentDataValues[valueType] = value

	def updateHistoryData(self, valueType, value):
		self.sensorSum[valueType] += value
		self.sensorNum[valueType] += 1

	#Functions to execute at a determined time	

	def updateCurrentDataFile(self):
                data = {"newtUpdate" : self.alarms.getNextUpdateStr('updateCurrentData'), "data": self.currentDataValues}
                	        
                with open(self.currentDataFile, 'w+') as f:
                    json.dump(data, f)

                logger.info('Updated current data file')

	def updateHistory(self):
		newValues = {'date' : getDatetime()}
		nullKeys = []
		for elem in self.sensorSum.keys():
			if self.sensorNum[elem] == 0:
				newValues[elem] = None
				nullKeys.append(elem)
			else:
				newValues[elem]= round(self.sensorSum[elem]/self.sensorNum[elem], 1)

		if len(nullKeys) != 0:
			logger.warning('-History update- No data received for %s', ', '.join(nullKeys))
		
		logger.info('-History update- %s', ', '.join("%s:%i" % (k,v) for k,v in self.sensorNum.items()))

		# Update database
		self.dbc.insertDataEntry(self.historyDataName, newValues)

		# Update json file
		if self.historyJson:
			nextUpdate = self.alarms.getNextUpdateStr('updateHistory')
			updateJsonFile(self.historyJsonFilePath, self.historyJsonDataHeader, newValues, nextUpdate)
		logger.info('Inserted data to history')

		# Reset data
		self.sensorSum = dict.fromkeys(self.sensorSum, 0)
		self.sensorNum = dict.fromkeys(self.sensorNum, 0)

	def updateDailyHistory(self):
		# Query to database
		lastDay = datetime.date.today() - datetime.timedelta(days=1)
		minVal = datetime.datetime.combine(lastDay, datetime.datetime.min.time())
		maxVal = datetime.datetime.combine(lastDay, datetime.datetime.max.time())
		data = self.dbc.queryBetweenValues(self.historyDataName, 'date', formatDatetime(minVal), formatDatetime(maxVal))
		dailyData = dict.fromkeys(self.dbDailyHistoryHeader, 0)
		dailyData['date'] = lastDay.strftime("%Y-%m-%d")
		numValues = dict.fromkeys(self.sensorTypes, 0)

		# Initialization of dailyData
		for column in dailyData:
			if 'MIN' in column:
				dailyData[column] = float('inf')
			elif 'MAX' in column:
				dailyData[column] = float('-inf')
			elif 'AVG' in column:
				dailyData[column] = 0.

		# Calculus of MIN, MAX and addition of all values to AVG
		for entry in data:
			for key,value in entry.items():
				if key != 'date' and value != None:
					dailyData[key + 'MIN'] = min(dailyData[key + 'MIN'], value)
					dailyData[key + 'MAX'] = max(dailyData[key + 'MAX'], value)
					dailyData[key + 'AVG'] += value
					numValues[key] += 1

		# Calculus of AVG
		for key in self.sensorTypes.keys():
			if numValues[key] != 0:
				dailyData[key + 'AVG'] = dailyData[key + 'AVG']/numValues[key]
			else:
				# there is no value registered for this sensor in 'lastDay'
				dailyData[key + 'AVG'] = None
				dailyData[key + 'MIN'] = None
				dailyData[key + 'MAX'] = None

		self.dbc.insertDataEntry(self.dailyHistoryDBName, dailyData)

		# Update json file
		if self.dailyHistoryJson:
			nextUpdate = self.alarms.getNextUpdateStr('updateDailyHistory')
			updateJsonFile(self.dailyHistoryJsonFilePath, self.dailyHistoryJsonDataHeader, dailyData, nextUpdate, True)
		logger.info('Inserted data to daily history')

	def run(self):
		while True:

			# Read data from Arduino and update the partial data
			data = self.ard.readInput()

			# Execute functions when it gets new data
			for (sensor,value) in data:
				if sensor in self.sensorNamesList:
					valueType = self.sensorData[sensor]
					for f in self.newValueFunctions:
						f(valueType, value)
					printSensor(sensor, value)

			# Execute functions when it is necessary
			toDo = self.alarms.getThingsToDo()
			for func in toDo:
				func()

			# Read from terminal
			inp = self.t.readLine()
			if inp != "":
				self.ard.write(inp)

			time.sleep(0.1)

if __name__ == '__main__':
	s = station()
	s.run()

		
