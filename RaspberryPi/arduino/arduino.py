#!/usr/bin/python

from time import sleep

class arduino:

	def __init__(self, connType, options, sensors):
		self.connTypes = {'433mhz' : self.initvw433mhzConn, 'usb' : self.initusbConn}

		self.connTypes[connType](options)
		self.sensors = sensors
		self.func = {"FLOAT": float, "INTEGER": int}

	def initvw433mhzConn(self, options):
		from arduino import vw433mhzConn
		self.conn = vw433mhzConn.vw433mhzConn(options)

	def initusbConn(self, options):
		from arduino import usbConn
		self.conn = usbConn.usbConn(options)

	def readInt(self):
		return int(self.readFloat())

	def readFloat(self):
		return float(self.readStrings())

	def readStrings(self):
		return self.conn.read()

	def readInput(self):
		strings = self.readStrings()
		allData = []
		for string in strings:
			data = string.split('_')
			if (len(data) == 2):
				sensor = data[0]
				value = data[1]
				try:
					value = self.func[self.sensors[sensor]](value)	#Changing type
					allData.append((sensor,value))
				except ValueError:
					print("Not valid input:", strings)
			else:
				print ("Not valid input:", strings)
		return allData
				

	def write(self, s):
		com = s.split()
		for elem in com:
			act = str.encode(elem + '\n')
			self.ser.write(act)
