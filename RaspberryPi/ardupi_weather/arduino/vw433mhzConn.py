#!/usr/bin/env python3

from ardupi_weather.arduino import vw
import pigpio
from time import time

class vw433mhzConn:

	 """
    Class in charge of the reading the data using 433mhz receiver.

    It uses the library https://github.com/joan2937/pigpio to do the transmission of the data. The vw import
    makes reference to the vw.py script in this library. It needs the pigpio daemon executing to work properly.
    """

	def __init__(self, options):

		"""
        Initialization of the 433mhz connexion.

        Args:
            options: Is a dictionary, it must have a 'enableRepetitions' key containing if the transceiver will
            	send more than one time the results of a sensor, and 'maxRepetitionTime', if more than one
            	results is send for a single sensor in 'maxRepetitionTime', only the first one will be send as
            	a result.
        """

		self.pi = pigpio.pi() # Connect to local Pi.
		self.rx = vw.rx(self.pi, options['rxPin'], options['bps']) # Specify Pi, rx gpio, and baud.
		if options['enableRepetitions']:
			self.enableRepetitions = True
			self.maxRepetitionTime = options['maxRepetitionTime']
			self.lastValue = None
			self.lastTime = 0
		else:
			self.enableRepetitions = False

	def read(self):

		"""
        Read all the available data.

        Returns:
            A list of received strings without repetitions.
        """

		data = []
		while self.rx.ready():
			msg = "".join(chr (c) for c in self.rx.get())
			if self.enableRepetitions:
				if msg != self.lastValue or time() >= self.lastTime + self.maxRepetitionTime:
					data.append(msg)
					self.lastValue = msg
					self.lastTime = time()
			else:
				data.append(msg)
		return data

