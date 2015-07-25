from arduino import vw
import pigpio
from time import time

class vw433mhzConn:
	def __init__(self, options):
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
		msg = ""
		if self.rx.ready():
			msg = "".join(chr (c) for c in self.rx.get())
			if self.enableRepetitions:
				if msg == self.lastValue and time() < self.lastTime + self.maxRepetitionTime:
					msg = ""
				else:
					self.lastValue = msg
					self.lastTime = time()
		return msg
		
