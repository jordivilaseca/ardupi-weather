#!/usr/bin/python

from arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
import datetime
import time
import yaml
import json

def getDatetime():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def getDate():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def formatDatetime(date):
	return date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def getPath(path, fileName):
	defaultPath = os.path.dirname(os.path.realpath(__file__)) + '/data'
	newPath = defaultPath if path == 'default' else path
	return newPath + '/' + fileName

def jsonTimestamp(stringTime):
	return time.mktime(datetime.datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S.%f').timetuple())*1000

def updateJsonFiles(jsonHistoryFilesPath, jsonHistoryFiles, valuesDict):
	for f in jsonHistoryFiles:
		filePath = getPath(jsonHistoryFilesPath, f) + '.json'

		# check if the file exists, in case it does not exists we create it
		if not os.path.exists(filePath):
			with open(filePath, 'w+') as jsonFile:
				jsonFile.write('[]')

		# update data
		with open(filePath, 'r') as jsonFile:
			data = json.load(jsonFile)
		data.append([jsonTimestamp(valuesDict['date']),valuesDict[f]])
		with open(filePath, 'w') as jsonFile:
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

		with open("config.yml", 'r') as ymlfile:
			cfg = yaml.load(ymlfile)

		self.sensorData = cfg['arduino']['sensors']
		self.sensorNamesList = list(self.sensorData.keys())

		self.sensorTypes = cfg['database']['values']
		self.sensorUnits = {key: self.sensorTypes[value] for key,value in self.sensorData.items()}		

		#Configure arduino
		arduinoCfg = cfg['arduino']
		self.configureArduino(arduinoCfg)

		#Configure database
		databaseCfg = cfg['database']
		self.configureDatabase(databaseCfg)

		#Initialize history database
		historyCfg = databaseCfg['historyDB']
		self.initialitzeHistoryDatabase(historyCfg)

		#Initialize daily history database
		dailyHistoryCfg = databaseCfg['dailyHistoryDB']
		self.initializeDailyHistoryDatabase(dailyHistoryCfg, historyCfg)

		#Initialize last sensor values record
		currentDataCfg = databaseCfg['currentData']
		self.initialitzeCurrentData(currentDataCfg)

		#configure station for webserver support
		webserverCfg = cfg['webserver']
		self.configureWebserverSupport(webserverCfg, historyCfg, dailyHistoryCfg, currentDataCfg)

		#Initialize terminal input
		self.t = terminal()

	#Configuration functions

	def configureArduino(self, ard):
		connection = ard['usedConnection']
		if connection == 'usb':
			usb = ard['usb']
			self.ard = arduino(usb['port'], usb['baud'], self.sensorUnits)
		else:
			print ('Unknown arduino connection')

	def configureDatabase(self, database):
		self.databaseName = database['name']

		usedDatabase = database['used']
		db = database[usedDatabase]
		if usedDatabase == 'sqlite':
			self.dbc.enableSqlite(getPath(db['path'], self.databaseName))
		elif usedDatabase == 'mongo':
			self.dbc.enableMongo(self.databaseName, db['server'], db['port'])
		else:
			'Unknown database name'

	def initialitzeHistoryDatabase(self, history):
		if history['enable']:
			self.dbHistoryHeader = {'date' : 'TEXT'}
			self.dbHistoryHeader.update(self.sensorTypes)

			self.historyDBName = history['name']
			self.dbc.createDataContainer(self.historyDBName, self.dbHistoryHeader)
			self.sensorSum = dict.fromkeys(self.sensorTypes, 0)
			self.sensorNum = dict.fromkeys(self.sensorTypes, 0)

			update = history['updateEvery']
			self.alarms.add('updateHistory', update['d'], update['h'], update['m'], update['s'])
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

			self.alarms.addDaily('updateDailyHistoryDatabase')
			self.generalFunctions['updateDailyHistoryDatabase'] = self.updateDailyHistoryDatabase

	def initialitzeCurrentData(self, currentData):
		if currentData['enable']:
			self.currentDataFile = getPath(currentData['path'], currentData['name'])

			self.currentDataValues = {}

			update = currentData['updateEvery']
			self.alarms.add('updateCurrentData', update['d'], update['h'], update['m'], update['s'])
			self.generalFunctions['updateCurrentData'] = self.updateCurrentDataFile

			self.newValueFunctions.append(self.updateCurrentData)

	def configureWebserverSupport(self, webserver, history, dailyHistory, currentData):
		if webserver['enable']:
			if not (history['enable'] and dailyHistory['enable'] and currentData['enable']):
				print("webserver cannot ben enabled because 'history' or 'dailyHistory' or 'currentData' are not enabled")
				return

			self.configureWebserverCharts(webserver['charts'])

	def configureWebserverCharts(self, charts):

		# Configure structures for history chart
		historyChart = charts['history']
		if historyChart['enable']:
			self.jsonHistoryFilesPath = historyChart['path']
			self.jsonHistoryFiles = []
			for panel in historyChart['panels']:
				self.jsonHistoryFiles.extend(list(panel['values']))
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

		# Set next update
		self.alarms.update(['updateCurrentData'])

	def updateHistory(self):
		valuesDict = processSensors(self.sensorSum, self.sensorNum)

		# Update database
		self.dbc.insertDataEntry(self.historyDBName, valuesDict)

		# Update json file
		if self.jsonHistory:
			updateJsonFiles(self.jsonHistoryFilesPath, self.jsonHistoryFiles, valuesDict)
		print('Inserted data to history')

		# Reset data
		self.sensorSum = dict.fromkeys(self.sensorSum, 0)
		self.sensorNum = dict.fromkeys(self.sensorNum, 0)

		# Set next update
		self.alarms.update(['updateHistory'])

	def updateDailyHistoryDatabase(self):
		# Query to database
		lastDay = datetime.date.today() - datetime.timedelta(days=1)
		minVal = datetime.datetime.combine(lastDay, datetime.datetime.min.time())
		maxVal = datetime.datetime.combine(lastDay, datetime.datetime.max.time())
		data = self.dbc.queryBetweenValues(self.historyDBName, 'date', formatDatetime(minVal), formatDatetime(maxVal))
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

		# set next update
		self.alarms.update(['updateDailyHistoryDatabase'])

	def run(self):
		while True:

			# Read data from Arduino and update the partial data
			sensor, value = self.ard.readInput()

			# Execute functions when it gets new data
			if (len(sensor) > 0):
				if sensor in self.sensorNamesList:
					valueType = self.sensorData[sensor]
					for f in self.newValueFunctions:
						f(valueType, value)
					printSensor(sensor, value)

			# Execute functions when it is necessary
			toDo = self.alarms.getThingsToDo()
			for idFunc in toDo:
				self.generalFunctions[idFunc]()

			# Read from terminal
			inp = self.t.readLine()
			if inp != "":
				self.ard.write(inp)

			time.sleep(0.1)

if __name__ == '__main__':
	s = station()
	s.run()

		
