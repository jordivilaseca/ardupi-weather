#!/usr/bin/env python

##########################################

import time
from RF24 import *

pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]

class nrf24l01pConn:
    def __init__(self, options):
        # Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz (RPi B+ and B 2)
        self.radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

        self.radio.begin()
        self.radio.enableDynamicPayloads()
        self.radio.setRetries(5,options['repetitions'])

        self.radio.openWritingPipe(pipes[1])
        self.radio.openReadingPipe(1,pipes[0])
        self.radio.startListening()

    def read(self):
        data = []
        while self.radio.available():
            len = self.radio.getDynamicPayloadSize()
            data.append(radio.read(len))
        return data

