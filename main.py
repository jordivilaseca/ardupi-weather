#!/usr/bin/python

import arduino
import database 
import os
from datetime import datetime

def getTime():
	return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

tableName = "prova"
table = ["date TEXT PRIMARY KEY", "sensorType TEXT", "sensor TEXT", "value TEXT"]
variables = ["date", "sensorType", "sensor", "value"]

arduinoPort = "ttyACM0"
arduinoBaud = 9600
DBpath = os.path.dirname(os.path.realpath(__file__)) + "/database/prova"

db = database.database(DBpath)
db.createTable(tableName, variables)
ard = arduino.arduino(arduinoPort, arduinoBaud)

while True:
	inp = ard.readInput()
	if (inp[2] != "error"):
		date = getTime()
		print (date)
		values = [date, inp[0], inp[1], inp[2]]
		db.insert(tableName, variables, values)
