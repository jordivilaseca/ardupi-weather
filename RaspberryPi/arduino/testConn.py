import random
from time import time

class testConn:
    MEAN_MIN = -100
    MEAN_MAX = 100
    STAND_DEVIATION_MIN = 1
    STAND_DEVIATION_MAX = 50
    EVERY_MIN = 20
    EVERY_MAX = 90

    def __init__(self, options):
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
        return random.uniform(testConn.MEAN_MIN, testConn.MEAN_MAX)

    def getStandDeviation(self):
        return random.uniform(testConn.STAND_DEVIATION_MIN, testConn.STAND_DEVIATION_MAX)

    def getEvery(self):
        return random.uniform(testConn.EVERY_MIN, testConn.EVERY_MAX)

    def read(self):
        data = []
        for i in range(len(self.names)):
            if self.next[i] < time():
                value = random.gauss(self.means[i], self.standDeviations[i])
                if self.isInt[i]:
                    value = int(value)
                data.append(self.names[i] + "_" + str(value))
                self.next[i] = self.next[i] + self.every[i]
        return data