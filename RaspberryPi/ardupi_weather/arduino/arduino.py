#!/usr/bin/env python3

from time import sleep

class Arduino:

	"""
	Class dealing with the different communication methods and the parsing of the data.
	"""

	def __init__(self, connType, options, sensors):

		"""
		Initialization of the Arduino.

		It initializes the selected connexion and stores all the necessary data to deal with
		the received data.

		Args:
			connType: Type of connexion to be used.
			options: Dictionary containing all the options for the connType.
			sensors: Dictionary containing sensor ids and the type of data that must return.
		"""

		self.connTypes = {
			'433mhz' : self.initvw433mhzConn,
			'usb' : self.initusbConn,
			'nrf24l01p' : self.initnrf24l01p,
			'test': self.initTestConn
		}

		self.connTypes[connType](options)
		self.sensors = sensors
		self.func = {"FLOAT": float, "INTEGER": int}

	def initvw433mhzConn(self, options):

		"""
		Initialization of the 433 MHz connexion.

		Args:
			options: Dictionary containing all the options for the connexion.
		"""

		from ardupi_weather.arduino import vw433mhzConn
		self.conn = vw433mhzConn.vw433mhzConn(options)

	def initusbConn(self, options):

		"""
		Initialization of the USB connexion.

		Args:
			options: Dictionary containing all the options for the connexion.
		"""

		from ardupi_weather.arduino.usbConn import USBConn
		self.conn = USBConn(options)

	def initnrf24l01p(self, options):

		"""
		Initialization of the 2.4 GHz connexion.

		Args:
			options: Dictionary containing all the options for the connexion.
		"""

		from ardupi_weather.arduino.nrf24l01pConn import nrf24l01pConn
		self.conn = nrf24l01pConn(options)

	def initTestConn(self, options):

		"""
		Initialization of the test connexion.

		Args:
			options: Dictionary containing all the options for the connexion.
		"""

		from ardupi_weather.arduino.testConn import TestConn
		self.conn = TestConn(options)

	def readInts(self):

		"""
		It reads all the available values as integers.

		In case that they are decimal, the values are truncated.

		Returns:
			A list with zero or more integers.

		Raises:
			ValueError: At least one of the received values is neither integer nor decimal.
		"""

		try:
			return int(self.readFloats())
		except ValueError:
			raise ValueError("The received value from the Arduino is not an integer")


	def readFloats(self):

		"""
		It reads all the available values as floats.

		Returns:
			A list with zero or more floats.

		Raises:
			ValueError: At least one of the received values is not a decimal.
		"""

		try:
			return float(self.readStrings())
		except ValueError:
			raise ValueError("The received value from the Arduino is not a decimal")

	def readStrings(self):

		"""
		It reads all the available values as strings.

		Returns:
			A list with zero or more strings.

		Raises:
			Exception: Error receiving a value.
		"""

		try:
			return self.conn.read()
		except Exception:
			raise Exception("Error receiving a value from the Arduino")

	def readInput(self):

		"""
		It reads all the available commands.

		The commands must have the following structure <sensorId>_<value>. The function looks
		if the command is well formatted and if the sensor_id is valid, if the two conditions
		are achieved the command is returned.

		Returns:
			A list of tuples, the tuples contain a sensorID and its value.

		"""

		strings = self.readStrings()
		allData = []
		for string in strings:
			data = string.split('_')
			sensor = data[0]
			if (len(data) == 2 and sensor in self.sensors.keys()):
				value = data[1]
				try:
					value = self.func[self.sensors[sensor]](value)	#Changing the value type
					allData.append((sensor,value))
				except Exception as e:
					print(str(e))
			else:
				print("Not valid input:", string)
		return allData
