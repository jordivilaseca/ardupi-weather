#!/usr/bin/python

import struct
from time import sleep
import serial

def readBytes():
	result = ser.readline()
	return result[0:len(result)-2]

def readInt():
	return int(readFloat())

def readFloat():
	return float(readString())

def readString():
	return readBytes().decode("utf-8")

def readInput():
	sensor = readString()
	sensorId = getSensorId(sensor)
	if sensorId == "lm35":
		print (sensor, readFloat(), "ºC")
	elif sensorId == "ldr":
		x = readInt()/1023
		print (sensor, format(x, '.3f'), "%")

def getSensorId(sensor):
	return sensor.split("_")[0]

ser = serial.Serial('/dev/ttyACM0', 9600) # Establish the connection on a specific port

while True:
     readInput()
