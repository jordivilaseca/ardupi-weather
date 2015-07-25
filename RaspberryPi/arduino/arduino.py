#!/usr/bin/python

from time import sleep
from arduino import vw433mhzConn
from arduino import usbConn

class arduino:

	def __init__(self, connType, options, sensors):
		self.connTypes = {'433mhz' : vw433mhzConn.vw433mhzConn, 'usb' : usbConn.usbConn}
		self.conn = self.connTypes[connType](options)
		self.sensors = sensors
		self.func = {"FLOAT": float, "INTEGER": int}
		
	def readBytes(self):
		return self.conn.read()

	def readInt(self):
		return int(self.readFloat())

	def readFloat(self):
		return float(self.readString())

	def readString(self):
		return self.readBytes().decode("utf-8")

	def readInput(self):
		rawData = self.readString()
		if (len(rawData) > 0):
			data = rawData.split('_')
			if (len(data) == 2):
				sensor = data[0]
				value = data[1]
				try:
					value = self.func[self.sensors[sensor]](value)	#Changing type
					return [sensor,value]
				except ValueError:
					print("Not valid input:", rawData)
					return ["",""]
			else:
				print ("Not valid input:", rawData)
				return ["",""]
		else:
			return ["",""]
				

	def write(self, s):
		com = s.split()
		for elem in com:
			act = str.encode(elem + '\n')
			self.ser.write(act)
