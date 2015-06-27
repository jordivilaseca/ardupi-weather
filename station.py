#!/usr/bin/python

import arduino
from database import database 
import os
from terminal import terminal
from myTime import myTime
from datetime import datetime
import time

def getFullDate():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def printSensor(sensor, valueType, value):
	date = getFullDate()
	print (date, sensor, value, sensorUnit[valueType])

def printDump(dumpId, rawDump, value):
	print ('-'*50)
	if rawDump == "dump_pin":
		sensor, sensorType, time, pin = value.split()
		print ("sensor %s, type %s, updateTime %s, pin %s" % (sensor, sensorType, time, pin))

	print ('-'*50)

def processSensors(sensSum, sensNum, sensList, partialList):
	for elem in sensList:
		partialList.append(sensSum[elem]/sensNum[elem])
	return partialList

myT = myTime(0,3,0)

sensorUnits = {"T": "float", "H": "float", "P": "float", "HI": "float"}

# To do average of sensors
sensorSum = {"T" : 0, "H" : 0, "HI" : 0, "P" : 0}
sensorNum = {"T" : 0, "H" : 0, "HI" : 0, "P" : 0}
sensorValueList = ["T", "H", "HI", "P"]

sensorUnit = {'T' : 'ºC', 'P' : 'Pa', 'H': '% humidity', 'HI': 'ºC'}
# DataBase prova
DBpath = os.path.dirname(os.path.realpath(__file__)) + "/database/prova"
tableName = "prova"
table = ["date TEXT PRIMARY KEY", "sensorType TEXT", "sensor TEXT", "value TEXT"]
tableVariables = ["date", "sensorType", "sensor", "value"]

#DataBase prova2
DBpath2 = os.path.dirname(os.path.realpath(__file__)) + "/database/prova2"
tableName2 = "newSensors"
table2 = ["date TEXT PRIMARY KEY", "Temperature FLOAT", "Humidity FLOAT", "HeatIndex INTEGER", "Pressure FLOAT"]
tableVariables2 = ["date", "Temprerature", "Humidity", "HeatIndex", "Pressure"]


# Arduino info
aPort = "ttyACM0"
aBaud = 57600

#db = database(DBpath)
#db.createTable(tableName, tableVariables)

db = database(DBpath2)
db.createTable(tableName2, tableVariables2)

ard = arduino.arduino(aPort, aBaud, sensorUnits)

t = terminal()

while True:
	sensor, valueType, value = ard.readInput()
	if (len(sensor) > 0):
		if valueType in sensorValueList:
			sensorSum[valueType] += value
			sensorNum[valueType] += 1
			printSensor(sensor, valueType, value)

	if (myT.isUpdateTime()):
		date = getFullDate()
		db.insert(tableName2, tableVariables2, processSensors(sensorSum, sensorNum, sensorValueList, [date]))

		# Reset data
		sensorSum = dict.fromkeys(sensorSum, 0)
		sensorNum = dict.fromkeys(sensorNum, 0)

		# Set next update
		myT.update()

	inp = t.readLine()
	if inp != "":
		ard.write(inp)
	time.sleep(0.1)

		
