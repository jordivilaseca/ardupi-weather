#!/usr/bin/python

from time import sleep

class arduino:

	def __init__(self, connType, options, sensors):
		self.connTypes = {'433mhz' : self.initvw433mhzConn, 'usb' : self.initusbConn, 'nrf24l01p' : self.initnrf24l01p}

		self.connTypes[connType](options)
		self.sensors = sensors
		self.func = {"FLOAT": float, "INTEGER": int}

	def initvw433mhzConn(self, options):
		from arduino import vw433mhzConn
		self.conn = vw433mhzConn.vw433mhzConn(options)

	def initusbConn(self, options):
		from arduino import usbConn
		self.conn = usbConn.usbConn(options)

	def initnrf24l01p(self, options):
		from arduino import nrf24l01pConn
		self.conn = nrf24l01pConn.nrf24l01pConn(options)

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
			sensor = data[0]
			if (len(data) == 2 and sensor in self.sensors.keys()):
				value = data[1]
				try:
					value = self.func[self.sensors[sensor]](value)	#Changing type
					allData.append((sensor,value))
				except ValueError:
					print("Not valid input:", string)
			else:
				print ("Not valid input:", string)
		return allData
				

	def write(self, s):
		com = s.split()
		for elem in com:
			act = str.encode(elem + '\n')
			self.ser.write(act)
