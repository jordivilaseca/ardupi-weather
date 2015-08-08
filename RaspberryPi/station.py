#!/usr/bin/python

from config import cfg, dataPath
from arduino.arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
import datetime
import time
import json

def getDatetime():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def getDate():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def formatDatetime(date):
	return date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def jsonTimestamp(stringTime):
	return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S.%f').timetuple())*1000

def updateJsonFiles(historyJsonFile, historyJsonData, valuesDict):
	# Read data
	with open(historyJsonFile, 'r') as jsonFile:
		data = json.load(jsonFile)

	# Update data dictionary
	lData = [valuesDict[key] for key in historyJsonData]
	data.append([jsonTimestamp(valuesDict['date']),lData])

	# Update file
	with open(historyJsonFile, 'w') as jsonFile:
		json.dump(data, jsonFile)

def printSensor(sensor, value):
	date = getDatetime()
	print (date, sensor, value)

def processSensors(sensSum, sensNum):
	d = {'date' : getDatetime()}
	for elem in sensSum.keys():
		d[elem]= round(sensSum[elem]/sensNum[elem], 1)
	return d

class station:
	def __init__(self):
		self.dbc = databaseController.databaseController()
		self.generalFunctions = {}
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
			self.alarms.add(self.updateHistory, update['d'], update['h'], update['m'], update['s'])
			self.generalFunctions['updateHistory'] = self.updateHistory

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

			self.alarms.addDaily(self.updateDailyHistoryDatabase)
			self.generalFunctions['updateDailyHistoryDatabase'] = self.updateDailyHistoryDatabase

	def initialitzeCurrentData(self, currentData):
		if currentData['enable']:
			self.currentDataFile = currentData['path'] + "currentData.json"

			self.currentDataValues = {}

			update = currentData['updateEvery']
			self.alarms.add(self.updateCurrentDataFile, update['d'], update['h'], update['m'], update['s'])
			self.generalFunctions['updateCurrentData'] = self.updateCurrentDataFile

			self.newValueFunctions.append(self.updateCurrentData)

	def configureWebserverSupport(self, webserver, history, dailyHistory):
		if webserver['enable']:
			if not (history['enable'] and dailyHistory['enable']):
				print("webserver cannot be enabled because 'history' or 'dailyHistory' are not enabled")
				return

			self.configureWebserverCharts(webserver['charts'])
			self.initialitzeCurrentData(webserver['liveData'])

	def configureWebserverCharts(self, charts):

		# Configure structures for history chart
		historyChart = charts['history']
		if historyChart['enable']:
			self.historyJsonFile = dataPath + 'history.json'

			# check if the file exists, in case it does not exists we create it
			if not os.path.exists(self.historyJsonFile):
				with open(self.historyJsonFile, 'w+') as jsonFile:
					jsonFile.write('[]')

			self.historyJsonData = []
			for panel in historyChart['panels']:
				self.historyJsonData.extend(list(panel['values']))
			self.jsonHistory = True
		else:
			self.jsonHistory = False

	#Functions to execute when a new sensor value arrives
	def updateCurrentData(self, valueType, value):
		self.currentDataValues[valueType] = value

	def updateHistoryData(self, valueType, value):
		self.sensorSum[valueType] += value
		self.sensorNum[valueType] += 1

	#Functions to execute at a determined time	

	def updateCurrentDataFile(self):
		with open(self.currentDataFile, 'w+') as f:    
			json.dump(self.currentDataValues, f)

		print('Updated current data file')

	def updateHistory(self):
		valuesDict = processSensors(self.sensorSum, self.sensorNum)

		# Update database
		self.dbc.insertDataEntry(self.historyDataName, valuesDict)

		# Update json file
		if self.jsonHistory:
			updateJsonFiles(self.historyJsonFile, self.historyJsonData, valuesDict)
		print('Inserted data to history')

		# Reset data
		self.sensorSum = dict.fromkeys(self.sensorSum, 0)
		self.sensorNum = dict.fromkeys(self.sensorNum, 0)

	def updateDailyHistoryDatabase(self):
		# Query to database
		lastDay = datetime.date.today() - datetime.timedelta(days=1)
		minVal = datetime.datetime.combine(lastDay, datetime.datetime.min.time())
		maxVal = datetime.datetime.combine(lastDay, datetime.datetime.max.time())
		data = self.dbc.queryBetweenValues(self.historyDataName, 'date', formatDatetime(minVal), formatDatetime(maxVal))
		dailyData = dict.fromkeys(self.dbDailyHistoryHeader, 0)
		dailyData['date'] = lastDay

		# Calculus of MIN, MAX and addition of all values to AVG
		i=0
		for entry in data:
			for key,value in entry.items():
				if key != 'date':
					if i == 0:
						dailyData[key + 'MIN'] = value
						dailyData[key + 'MAX'] = value
						dailyData[key + 'AVG'] = value
					else:
						dailyData[key + 'MIN'] = min(dailyData[key + 'MIN'], value)
						dailyData[key + 'MAX'] = max(dailyData[key + 'MAX'], value)
						dailyData[key + 'AVG'] += value
			i += 1

		# Calculus of AVG
		for key in self.sensorTypes.keys():
			dailyData[key + 'AVG'] = dailyData[key + 'AVG']/i

		self.dbc.insertDataEntry(self.dailyHistoryDBName, dailyData)
		print('Inserted data to daily history')

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

		
