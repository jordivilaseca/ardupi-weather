#!/usr/bin/python

from arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
from datetime import datetime
import time
import yaml

def getFullDate():
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

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
		self.functions = {}
		self.alarms = alarm()

		with open("config.yml", 'r') as ymlfile:
			cfg = yaml.load(ymlfile)

		self.sensorData = cfg['arduino']['sensors']
		self.sensorNamesList = list(self.sensorData.keys())

		units = cfg['database']['units']
		self.sensorUnits = {key: units[value] for key,value in self.sensorData.items()}
		self.sensorSum = dict.fromkeys(units, 0)
		self.sensorNum = dict.fromkeys(units, 0)

		self.dbHeaderUnits = {'Date' : 'TEXT'}
		self.dbHeaderUnits.update(units)

		#Configure arduino
		self.configureArduino(cfg['arduino'])

		#Configure database
		self.configureDatabase(cfg['database'])

		#Initialize history database
		self.initialitzeHistoryDatabase(cfg['database']['historyDB'])

		#Initialitze terminal input
		self.t = terminal()

	def updateHistoryData(self):
		valuesDict = processSensors(self.sensorSum, self.sensorNum)
		self.dbc.insertDataEntry(self.historyDBName, valuesDict)
		print('Inserted data to database')

		# Reset data
		self.sensorSum = dict.fromkeys(self.sensorSum, 0)
		self.sensorNum = dict.fromkeys(self.sensorNum, 0)

		# Set next update
		self.alarms.update(['updateHistoryData'])

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
			defaultPath = os.path.dirname(os.path.realpath(__file__)) + '/data'
			sqlitePath = defaultPath if db['path'] == 'default' else db['path']
			self.dbc.enableSqlite(sqlitePath + '/' + self.databaseName)
		elif usedDatabase == 'mongo':
			self.dbc.enableMongo(self.databaseName, db['server'], db['port'])
		else:
			'Unknown database name'

	def initialitzeHistoryDatabase(self, history):
		if history['enable']:
			self.dbc.createDataContainer(history['name'], self.dbHeaderUnits)

			self.historyDBName = history['name']

			update = history['updateEvery']
			self.alarms.add('updateHistoryData', update['d'], update['h'], update['m'], update['s'])
			self.functions['updateHistoryData'] = self.updateHistoryData

	def run(self):
		while True:

			# Read data from Arduino and update the partial data
			sensor, value = self.ard.readInput()
			if (len(sensor) > 0):
				if sensor in self.sensorNamesList:
					valueType = self.sensorData[sensor]
					self.sensorSum[valueType] += value
					self.sensorNum[valueType] += 1
					printSensor(sensor, value)

			# Execute functions when it is necessary
			toDo = self.alarms.getThingsToDo()
			for idFunc in toDo:
				self.functions[idFunc]()

			# Read from terminal
			inp = self.t.readLine()
			if inp != "":
				self.ard.write(inp)

			time.sleep(0.1)

if __name__ == '__main__':
	s = station()
	s.run()

		
