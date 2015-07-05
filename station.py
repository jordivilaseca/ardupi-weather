#!/usr/bin/python

from arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
from datetime import datetime
import time
import yaml
import json

def getFullDate():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def getPath(path, fileName):
	defaultPath = os.path.dirname(os.path.realpath(__file__)) + '/data'
	newPath = defaultPath if path == 'default' else path
	return newPath + '/' + fileName

def printSensor(sensor, value):
	date = getFullDate()
	print (date, sensor, value)

def processSensors(sensSum, sensNum):
	d = {'Date' : getFullDate()}
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

		self.units = cfg['database']['units']
		self.sensorUnits = {key: self.units[value] for key,value in self.sensorData.items()}		

		self.dbHeaderUnits = {'Date' : 'TEXT'}
		self.dbHeaderUnits.update(self.units)

		#Configure arduino
		self.configureArduino(cfg['arduino'])

		#Configure database
		self.configureDatabase(cfg['database'])

		#Initialize history database
		self.initialitzeHistoryDatabase(cfg['database']['historyDB'])

		#Initialize last sensor values record
		self.initialitzeCurrentData(cfg['database']['currentData'])

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
			self.dbc.createDataContainer(history['name'], self.dbHeaderUnits)
			self.historyDBName = history['name']
			self.sensorSum = dict.fromkeys(self.units, 0)
			self.sensorNum = dict.fromkeys(self.units, 0)

			update = history['updateEvery']
			self.alarms.add('updateHistoryDatabase', update['d'], update['h'], update['m'], update['s'])
			self.generalFunctions['updateHistoryDatabase'] = self.updateHistoryDatabase

			self.newValueFunctions.append(self.updateHistoryData)

	def initialitzeCurrentData(self, currentData):
		if currentData['enable']:
			self.currentDataFile = getPath(currentData['path'], currentData['name'])
			self.currentDataValues = {}

			update = currentData['updateEvery']
			self.alarms.add('updateCurrentData', update['d'], update['h'], update['m'], update['s'])
			self.generalFunctions['updateCurrentData'] = self.updateCurrentDataFile

			self.newValueFunctions.append(self.updateCurrentData)

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

	def updateHistoryDatabase(self):
		valuesDict = processSensors(self.sensorSum, self.sensorNum)
		self.dbc.insertDataEntry(self.historyDBName, valuesDict)
		print('Inserted data to database')

		# Reset data
		self.sensorSum = dict.fromkeys(self.sensorSum, 0)
		self.sensorNum = dict.fromkeys(self.sensorNum, 0)

		# Set next update
		self.alarms.update(['updateHistoryDatabase'])

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

		
