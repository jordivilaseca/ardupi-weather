import serial

class usbConn:
	def __init__(self, options):
		self.ser = serial.Serial("/dev/" + options['port'], options['baud'], timeout=0)

	def read(self):
		data = self.ser.readline()
		return data[0:-2].decode("utf-8") 			#Remove endline chars
