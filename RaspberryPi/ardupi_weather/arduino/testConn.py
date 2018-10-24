#!/usr/bin/env python3

import random
from time import time

class TestConn:

    """
    This class creates random values for the sensors used.

    Class used for testing purposes, the data is generated using a normal distribution with random mean
    and standard deviation. The time between two generated values for a sensor is random, but is fixed at
    the initialization of the class.
    """
    MEAN_MIN = -100
    MEAN_MAX = 100
    STAND_DEVIATION_MIN = 1
    STAND_DEVIATION_MAX = 50
    EVERY_MIN = 20
    EVERY_MAX = 90

    def __init__(self, options):

        """
        Initialization of the class.

        Here is where are fixed all the parameters for the random generation of the data. These parameters
        are different for all the sensors and are generated randomly.

        Args:
            options: It is a dictionary. For each one of its items, the key is a sensor ID and the value
                the type of data that it sends (FLOAT or INTEGER).
        """

        self.names = []
        self.means = []
        self.standDeviations = []
        self.every = []
        self.next = []
        self.isInt = []

        for key,value in options.items():
            self.names.append(key)
            self.means.append(self.getMean())
            self.standDeviations.append(self.getStandDeviation())
            self.every.append(self.getEvery())
            self.next.append(time())
            self.isInt.append(True if value == "INTEGER" else False)

    def getMean(self):

        """
        It calculates a random mean between MEAN_MIN and MEAN_MAX.

        Returns:
            The computed mean.
        """

        return random.uniform(testConn.MEAN_MIN, testConn.MEAN_MAX)

    def getStandDeviation(self):

        """
        It calculates a random standard deviation between STAND_DEVIATION_MIN and STAND_DEVIATION_MAX.

        Returns:
            The computed standard deviation.
        """

        return random.uniform(testConn.STAND_DEVIATION_MIN, testConn.STAND_DEVIATION_MAX)

    def getEvery(self):

        """
        It calculates a random time between two generated results for a sensor. It's value is between
        STAND_DEVIATION_MIN and STAND_DEVIATION_MAX.

        Returns:
            The computed time.
        """

        return random.uniform(testConn.EVERY_MIN, testConn.EVERY_MAX)

    def read(self):

        """
        It generates random results for the sensors that have passed enough time.

        Returns:
            A list of generated commands.
        """
        data = []
        for i in range(len(self.names)):
            if self.next[i] < time():
                value = random.gauss(self.means[i], self.standDeviations[i])
                if self.isInt[i]:
                    value = int(value)
                data.append(self.names[i] + "_" + str(value))
                self.next[i] = self.next[i] + self.every[i]
        return data
