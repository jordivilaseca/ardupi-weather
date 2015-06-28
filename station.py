#!/usr/bin/python

from arduino import arduino
from database import databaseController
import os
from terminal import terminal
from myTime import myTime
from datetime import datetime
import time

def getFullDate():
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def printSensor(sensor, value):
	date = getFullDate()
	print (date, sensor, value)

def processSensors(sensSum, sensNum, sensorList):
	d = {'DATE' : getFullDate()}
	for elem in sensorList:
		d[elem]= round(sensSum[elem]/sensNum[elem], 1)
	return d

def printDump(dumpId, rawDump, value):
	print ('-'*50)
	if rawDump == "dump_pin":
		sensor, sensorType, time, pin = value.split()
		print ("sensor %s, type %s, updateTime %s, pin %s" % (sensor, sensorType, time, pin))

	print ('-'*50)

def checkKeysDict(dic, keys):
	if all (keys in dic for key in keys):
	    return True
	else:
		return False

class station:
	def __init__(self, sensors):
		self.sensorUnits = sensors
		self.sensorSum = dict.fromkeys(sensors, 0)
		self.sensorNum = dict.fromkeys(sensors, 0)
		self.sensorValueList = list(sensors.keys())

		self.dbHeaderUnits = {'DATE' : 'TEXT'}
		self.dbHeaderUnits.update(self.sensorUnits)

		self.dbc = databaseController.databaseController()

		self.myT = myTime()

	def enableSqlitedb(self, path=os.path.dirname(os.path.realpath(__file__)) + "/data/weatherStationDB"):
		self.dbSensorsName = path.split('/')[-1]
		self.sqlitePath = path
		self.dbc.enableSqlitedb(path)

	def enableMongodb(self, dbName='weatherStationDB', server='localhost',port=27017):
		self.dbSensorsName = dbName
		self.dbc.enableMongodb(dbName, server, port)

	def enableUsbArduino(self, port, baud):
		self.dbc.createDataContainer('sensorsData', self.dbHeaderUnits)
		self.ard = arduino(port, baud, self.sensorUnits)

	def setTimeDatabaseUpdates(self, h, m, s):
		self.myT.setTimeUpdates(h, m, s)

	def run(self):
		t = terminal()

		while True:
			sensor, valueType, value = self.ard.readInput()
			if (len(sensor) > 0):
				if valueType in self.sensorValueList:
					self.sensorSum[valueType] += value
					self.sensorNum[valueType] += 1
					printSensor(sensor, value)

			if (self.myT.isUpdateTime()):
				valuesDict = processSensors(self.sensorSum, self.sensorNum, self.sensorValueList)
				self.dbc.insertDataEntry('sensorsData', valuesDict)
				print('Inserted data')

				# Reset data
				self.sensorSum = dict.fromkeys(self.sensorSum, 0)
				self.sensorNum = dict.fromkeys(self.sensorNum, 0)

				# Set next update
				self.myT.update()

			inp = t.readLine()
			if inp != "":
				self.ard.write(inp)
			time.sleep(0.1)

if __name__ == '__main__':
	sensorUnits = {'T': 'FLOAT', 'H' : 'FLOAT', 'P' : 'FLOAT', 'HI' : 'FLOAT'}
	
	s = station(sensorUnits)
	s.enableSqlitedb()
	s.setTimeDatabaseUpdates(0,5,0)
	s.enableUsbArduino('ttyACM0', 57600)
	s.run()

		
