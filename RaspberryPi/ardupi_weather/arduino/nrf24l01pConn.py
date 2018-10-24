#!/usr/bin/env python3

import time
from RF24 import *

class nrf24l01pConn:

    """
    Class in charge of the reading the data using nrf24l01p receiver.

    It uses the library https://github.com/TMRh20/RF24 to do the transmission of the data.
    """

    # Used pipes, they must be the same for the Arduino and the Raspberry Pi
    PIPES = [0xF0F0F0F0E1, 0xF0F0F0F0D2]

    def __init__(self, options):

        """
        Initialization of the nrf24l01p connexion.

        Args:
            options: Is a dictionary, it must have a 'repetitions' key. It is the maximum number of repetitions
                to do when you are sending a value and the receiver do not get it, the value must be between
                [1, 15].
        """

        # Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz (RPi B+ and B 2)
        self.radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

        self.radio.begin()
        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.enableDynamicPayloads()
        self.radio.setDataRate( RF24_250KBPS )
        self.radio.setRetries(5,options['repetitions'])

        self.radio.openWritingPipe(nrf24l01pConn.PIPES[1])
        self.radio.openReadingPipe(1,nrf24l01pConn.PIPES[0])
        self.radio.startListening()

    def read(self):

        """
        Read all the available data.

        Returns:
            A list of received strings.
        """

        data = []
        while self.radio.available():
            lenght = str(self.radio.getDynamicPayloadSize())
            data.append(self.radio.read(lenght))
        return data

