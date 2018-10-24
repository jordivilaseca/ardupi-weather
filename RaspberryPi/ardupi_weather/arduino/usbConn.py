import serial

class USBConn:

	"""
    Class in charge of the reading the data send through a USB.
    """

	def __init__(self, options):

		"""
        Initialization of the serial connexion.

        Args:
            options: Is a dictionary, it must have a 'port' key (containing the port where the Arduino
            	is connected), and a 'baud' key (containing the bauds).
        """

		self.ser = serial.Serial("/dev/" + options['port'], options['baud'],
								 timeout=0, parity=serial.PARITY_EVEN, bytesize=serial.EIGHTBITS,
								 stopbits=serial.STOPBITS_ONE)

	def read(self):

		"""
        Read all the available data.

        Returns:
            A list of received strings.
        """

		data = self.ser.readlines()
		return [d[0:-2].decode("utf-8") for d in data] 		#Remove endline chars.
