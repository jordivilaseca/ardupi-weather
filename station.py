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

def printSensor(sensorId, sensor, value):
	date = getFullDate()
	if sensorId == "lm35":
		print (date, sensor, value, "ºC")
	elif sensorId == "ldr":
		print (date, sensor, value, "%")

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

sensorsDic = {"lm35_19": "float", "lm35_23": "float", "ldr_21": "integer", "dump_pin": "string"}
types = ["float", "float", "integer"]

# To do average of sensors
sensorSum = {"lm35_19" : 0, "lm35_23" : 0, "ldr_21" : 0}
sensorNum = {"lm35_19" : 0, "lm35_23" : 0, "ldr_21" : 0}
sensorList = ["lm35_19", "lm35_23", "ldr_21"]

# DataBase prova
DBpath = os.path.dirname(os.path.realpath(__file__)) + "/database/prova"
tableName = "prova"
table = ["date TEXT PRIMARY KEY", "sensorType TEXT", "sensor TEXT", "value TEXT"]
tableVariables = ["date", "sensorType", "sensor", "value"]

#DataBase prova2
DBpath2 = os.path.dirname(os.path.realpath(__file__)) + "/database/prova2"
tableName2 = "prova2"
table2 = ["date TEXT PRIMARY KEY", "lm35_19 FLOAT", "lm35_23 FLOAT", "ldr_21 INTEGER"]
tableVariables2 = ["date", "lm35_19", "lm35_23", "ldr_21"]


# Arduino info
aPort = "ttyACM0"
aBaud = 57600

#db = database(DBpath)
#db.createTable(tableName, tableVariables)

db = database(DBpath2)
db.createTable(tableName2, tableVariables2)

ard = arduino.arduino(aPort, aBaud, sensorsDic)

t = terminal()

while True:
	idInput, rawInput, value = ard.readInput()
	if (idInput != "invalid" and len(idInput) > 0):
		if (idInput == "dump"):
			printDump(idInput, rawInput, value)
		else:
			if rawInput in sensorList:
				sensorSum[rawInput] += value
				sensorNum[rawInput] += 1
				printSensor(idInput, rawInput, value)

	if (myT.isUpdateTime()):
		date = getFullDate()
		db.insert(tableName2, tableVariables2, processSensors(sensorSum, sensorNum, sensorList, [date]))
		sensorSum = dict.fromkeys(sensorSum, 0)
		sensorNum = dict.fromkeys(sensorNum, 0)
		myT.update()

	inp = t.readLine()
	if inp != "":
		ard.write(inp)
	time.sleep(0.1)

		
