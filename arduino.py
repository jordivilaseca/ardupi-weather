#!/usr/bin/python

import struct
from time import sleep
import serial

class arduino:
	validInputs = ["lm35", "ldr", "dump"]

	def __init__(self, port, baud):
		self.port = port
		self.baud = baud
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
		rawInput = self.readString()
		idInput = self.getSensorId(rawInput)
		if (idInput not in self.validInputs and len(rawInput) > 0):
			print ("Not valid input: ", rawInput)
			return ["invalid", "invalid", "invalid"]
		else:
			value = self.readString()
			return [idInput, rawInput, value]

	def getSensorId(self, sensor):
		return sensor.split("_")[0]

	def write(self, s):
		com = s.split()
		for elem in com:
			act = str.encode(elem + '\n')
			self.ser.write(act)
