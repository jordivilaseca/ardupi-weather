from arduino import vw
import pigpio

class vw433mhzConn:
	def __init__(self, options):
		self.pi = pigpio.pi() # Connect to local Pi.
		self.rx = vw.rx(self.pi, options['rxPin'], options['bps']) # Specify Pi, rx gpio, and baud.

	def read(self):
		ret = ""
		if self.rx.ready():
			ret = "".join(chr (c) for c in self.rx.get())
		return ret
		
