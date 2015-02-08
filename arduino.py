#!/usr/bin/python

import struct
from time import sleep
import serial

class arduino:
	def __init__(self, port, baud):
		self.port = port
		self.baud = baud
		self.ser = serial.Serial("/dev/" + port, baud) # Establish the connection on a specific port
		
	def readBytes(self):
		result = self.ser.readline()
		return result[0:len(result)-2]

	def readInt(self):
		return int(self.readFloat())

	def readFloat(self):
		return float(self.readString())

	def readString(self):
		return self.readBytes().decode("utf-8")

	def readInput(self):
		sensor = self.readString()
		sensorId = self.getSensorId(sensor)
		value = "error"
		if sensorId == "lm35":
			value = self.readString()
			print (sensor, value, "ºC")
		elif sensorId == "ldr":
			value = str(format(self.readInt()/1023, '.3f'))
			print (sensor, value, "%")

		return [sensorId, sensor, value]

	def getSensorId(self, sensor):
		return sensor.split("_")[0]
