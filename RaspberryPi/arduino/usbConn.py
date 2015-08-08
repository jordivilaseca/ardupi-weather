import serial

class usbConn:
	def __init__(self, options):
		self.ser = serial.Serial("/dev/" + options['port'], options['baud'], timeout=0, parity=serial.PARITY_EVEN, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE)

	def read(self):
		data = self.ser.readlines()
		return [d[0:-2].decode("utf-8") for d in data] 		#Remove endline chars.
