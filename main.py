#!/usr/bin/python

import arduino
import database 
import os
import terminal
from datetime import datetime
import time

def getTime():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# Input: [date, sensorId, sensor, value]
def printSensor(date, sensorId, sensor, value):
	if sensorId == "lm35":
		print (date, sensor, value, "ºC")
	elif sensorId == "ldr":
		print (date, sensor, value, "%")

def printDump(dumpId, rawDump, value):
	print ('-'*50)
	if rawDump == "dump_pin":
		v = value.split()
		print ("sensor %s, type %s, updateTime %s, pin %s" % (v[0], v[1], v[2], v[3]))

	print ('-'*50)


tableName = "prova"
table = ["date TEXT PRIMARY KEY", "sensorType TEXT", "sensor TEXT", "value TEXT"]
tableVariables = ["date", "sensorType", "sensor", "value"]

arduinoPort = "ttyACM0"
arduinoBaud = 57600
DBpath = os.path.dirname(os.path.realpath(__file__)) + "/database/prova"

db = database.database(DBpath)
db.createTable(tableName, tableVariables)
ard = arduino.arduino(arduinoPort, arduinoBaud)

t = terminal.terminal()

while True:
	idInput, rawInput, value = ard.readInput()
	if (idInput != "invalid" and len(idInput) > 0):
		if (idInput == "dump"):
			printDump(idInput, rawInput, value)
		else:
			date = getTime()
			printSensor(date, idInput, rawInput, value)
			db.insert(tableName, tableVariables, [date, idInput, rawInput, value])

	inp = t.readLine()
	if inp != "":
		ard.write(inp)
	time.sleep(0.1)

		
