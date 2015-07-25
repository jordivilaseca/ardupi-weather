#!/usr/bin/python

import struct
from time import sleep
import serial

class arduino:

	def __init__(self, port, baud, sensors):
		self.port = port
		self.baud = baud
		self.sensors = sensors
		self.func = {"TEXT": self.readString, "FLOAT": self.readFloat, "INTEGER": self.readInt}
		self.ser = serial.Serial("/dev/" + port, baud, timeout=0) # Establish the connection on a specific port
		
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
		if (len(sensor) > 0):
			if (sensor in self.sensors):
				try:
					value = self.func[self.sensors[sensor]]()
					return [sensor,value]
				except ValueError:
					print ("Not valid input")
					return ["",""]
			else:
				print ("Not valid input: ", sensor)
		return ["",""]

	def write(self, s):
		com = s.split()
		for elem in com:
			act = str.encode(elem + '\n')
			self.ser.write(act)
