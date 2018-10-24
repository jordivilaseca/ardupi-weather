#!/usr/bin/env python3

from ardupi_weather.config import cfg, DATA_PATH, LOG_PATH
from ardupi_weather.arduino.arduino import Arduino
from ardupi_weather.database.databaseController import DatabaseController
import os
from ardupi_weather.terminal import Terminal
from ardupi_weather.alarm import Alarm
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import json

# Configuring the handler of the logger.
LOG_FILE = LOG_PATH + 'station.log'
handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=6)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

# Configuring the logger.
logger = logging.getLogger('station')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def getTimestamp():

    """
    It returns the current timestamp of the machine.

    Returns:
        An integer containing the current timestamp.
    """

    return int(time.mktime(datetime.datetime.now().timetuple()))*1000

def formatDatetime(date):

    """
    It return the timestamp of a concret date.

    Args:
        date: A datetime object.

    Returns:
        An integer containing the timestamp of a concrete date.
    """

    return int(time.mktime(date.timetuple()))*1000

def printSensor(sensor, value):

    """
    It shows the current time, a sensor and its value in the terminal.

    Args:
        sensor: Sensor identifier to be printed
        value: The value for the sensor.
    """

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print (date, sensor, value)

class Station:

    """
    Class dealing with the communications with an Arduino, processing of the data and its storing to a concrete
    database.

    It uses the information in config.yml to configure the station.
    """

    def __init__(self):

        """
        Initialization of the station. It includes the database and the Arduino.
        """

        self.dbc = DatabaseController()
        self.newValueFunctions = []
        self.alarms = Alarm()

        self.sensorData = cfg['arduino']['sensors']
        self.sensorNamesList = list(self.sensorData.keys())

        self.sensorTypes = cfg['data']['values']
        self.sensorUnits = {key: self.sensorTypes[value] for key,value in self.sensorData.items()}

        #Configure arduino
        arduinoCfg = cfg['arduino']
        self.configureArduino(arduinoCfg)

        #Configure database
        dataCfg = cfg['data']
        self.configureDatabase(dataCfg)

        #Initialize next updates database
        self.initializeNextUpdates()

        #Initialize history database
        historyCfg = dataCfg['history']
        self.initialitzeHistoryDatabase(historyCfg)

        #Initialize current data database
        currentDataCfg = dataCfg['currentData']
        self.initialitzeCurrentData(currentDataCfg)

        #Initialize daily history database
        dailyHistoryCfg = dataCfg['dailyHistory']
        self.initializeDailyHistoryDatabase(dailyHistoryCfg, historyCfg)

        #Initialize terminal input
        self.t = Terminal()

    ###########################
    # Configuration functions #
    ###########################

    def configureArduino(self, ard):

        """
        It configures an Arduino using the specified connection and its options.

        Args:
            ard: Arduino configuration.
        """

        connection = ard['usedConnection']
        if connection == 'test':
            self.ard = Arduino(connection, self.sensorUnits, self.sensorUnits)
        else:
            self.ard = Arduino(connection, ard[connection], self.sensorUnits)

    def configureDatabase(self, data):

        """
        It configures the desired type of database (mongodb or sqlite).

        Args:
            data: Database configuration.
        """

        databaseName = data['name']

        usedDatabase = data['usedDB']
        db = data[usedDatabase]
        if usedDatabase == 'sqlite':
            self.dbc.enableSqlite(db['path'] + databaseName)
        elif usedDatabase == 'mongo':
            self.dbc.enableMongo(databaseName, db['uri'], DATA_PATH, LOG_PATH)
        else:
            'Unknown database name'

    def initializeNextUpdates(self):

        """
        It configures the "nextUpdates" container. It has the next update time for currentData,
        history and dailyHistory containers.

        This information is used to make possible to the browsers to autoupdate the webpage data
        without refreshing the it.
        """

        self.dbc.createContainer('nextUpdates', {'name':'TEXT PRIMARY KEY','nextUpdate':'TEXT'})

    def initialitzeCurrentData(self, currentData):

        """
        It initializes the current data container of the database.

        Args:
            currentData: Current data configuration.
        """

        if currentData['enable']:
            self.currentDataDatabaseName = currentData['name']
            self.dbCurrentDataHeader = {'type':'TEXT PRIMARY KEY', 'value': 'TEXT'}

            self.currentDataValues = {}

            self.dbc.createContainer(self.currentDataDatabaseName, self.dbCurrentDataHeader)

            # Initialize current data database
            for key in self.sensorTypes.keys():
                self.dbc.upsert(self.currentDataDatabaseName, 'type', {'type':key, 'value':None})

            # Add update current data alarm
            update = currentData['updateEvery']
            self.alarms.add('updateCurrentData', self.updateCurrentDataDatabase, update['d'], update['h'], update['m'], update['s'])

            # Insert next update to database
            self.dbc.upsert('nextUpdates', 'name',  {'name':'currentData','nextUpdate': self.alarms.getNextUpdateStr('updateCurrentData')})

            self.newValueFunctions.append(self.updateCurrentData)

    def initialitzeHistoryDatabase(self, history):

        """
        It initializes the history container of the database.

        Args:
            history: History configuration.
        """

        if history['enable']:
            self.dbHistoryHeader = {'date' : 'TIMESTAMP'}
            self.dbHistoryHeader.update(self.sensorTypes)

            self.historyDataName = history['name']
            self.dbc.createContainer(self.historyDataName, self.dbHistoryHeader)

            self.sensorSum = dict.fromkeys(self.sensorTypes, 0)
            self.sensorNum = dict.fromkeys(self.sensorTypes, 0)

            update = history['updateEvery']
            self.alarms.add('updateHistory', self.updateHistoryDatabase, update['d'], update['h'], update['m'], update['s'])

            self.dbc.upsert('nextUpdates', 'name', {'name':'history','nextUpdate': self.alarms.getNextUpdateStr('updateHistory')})

            self.newValueFunctions.append(self.updateHistoryData)

    def initializeDailyHistoryDatabase(self, daily, history):

        """
        It initializes the daily history container of the database.

        Args:
            daily: Daily history configuration.
            history: History configuration.
        """

        if daily['enable']:
            if not history['enable']:
                print ("Daily history cannot be enabled because 'history' is not enabled")
                return

            self.dbDailyHistoryHeader = {'date' : 'TEXT'}
            self.dbDailyHistoryHeader.update({key + 'MAX': value for key,value in self.sensorTypes.items()})
            self.dbDailyHistoryHeader.update({key + 'MIN': value for key,value in self.sensorTypes.items()})
            self.dbDailyHistoryHeader.update({key + 'AVG': value for key,value in self.sensorTypes.items()})

            self.dailyHistoryDataName = daily['name']
            self.dbc.createContainer(self.dailyHistoryDataName, self.dbDailyHistoryHeader)

            self.alarms.addDaily('updateDailyHistory', self.updateDailyHistoryDatabase)

            self.dbc.upsert('nextUpdates', 'name',  {'name':'dailyHistory','nextUpdate': self.alarms.getNextUpdateStr('updateDailyHistory')})

    ########################################################
    # Functions to execute when a new sensor value arrives #
    ########################################################

    def updateCurrentData(self, valueType, value):

        """
        It updates the current value of a type of data.

        Args:
            valueType: The type of data to update.
            value: The new value.
        """

        self.currentDataValues[valueType] = value

    def updateHistoryData(self, valueType, value):

        """
        It updates intermediate history data.

        Args:
            valueType: The type of data to update.
            value: The new value.
        """

        self.sensorSum[valueType] += value
        self.sensorNum[valueType] += 1

    #############################################
    # Functions to execute at a determined time #
    #############################################

    def updateCurrentDataDatabase(self):

        """
        It updates the data of the current data database and the next updates database.
        """

        for (key,value) in self.currentDataValues.items():
            self.dbc.update(self.currentDataDatabaseName,{"value":value}, "type", key)

        # Change next update time
        nextUpdate = self.alarms.getNextUpdateStr('updateCurrentData')
        self.dbc.update("nextUpdates", {"nextUpdate":nextUpdate}, "name", "currentData")

        print('Updated current data file')

    def updateHistoryDatabase(self):

        """
        It updates the history database and the next updates database.

        The data stored in it is the mean of the received values from the last update to the moment
        this function is called.
        """

        # Compute means from the received values.
        newValues = {'date' : getTimestamp()}
        nullKeys = []
        for elem in self.sensorSum.keys():
            if self.sensorNum[elem] == 0:
                newValues[elem] = None
                nullKeys.append(elem)
            else:
                newValues[elem]= round(self.sensorSum[elem]/self.sensorNum[elem], 1)

        if len(nullKeys) != 0:
            logger.warning('-History update- No data received for %s', ', '.join(nullKeys))

        logger.info('-History update- %s', ', '.join("%s:%i" % (k,v) for k,v in self.sensorNum.items()))

        # Update database
        self.dbc.insert(self.historyDataName, newValues)

        # Change next update time
        nextUpdate = self.alarms.getNextUpdateStr('updateHistory')
        self.dbc.update("nextUpdates", {"nextUpdate":nextUpdate}, "name", "history")

        print('Inserted data to history')

        # Reset data
        self.sensorSum = dict.fromkeys(self.sensorSum, 0)
        self.sensorNum = dict.fromkeys(self.sensorNum, 0)

    def updateDailyHistoryDatabase(self):

        """
        It updates the daily history database and the next updates database.

        The mean, minimum and maximum values are computed from the history database. It means that usually
        the values of the minimum and maximum values will not be the correct ones, but an approximation.
        Using smaller updating time for the history involve having smaller errors in the daily history.
        """

        # Query to history database
        lastDay = datetime.date.today() - datetime.timedelta(days=1)
        minVal = datetime.datetime.combine(lastDay, datetime.datetime.min.time())
        maxVal = datetime.datetime.combine(lastDay, datetime.datetime.max.time())
        data = self.dbc.queryBetweenValues(self.historyDataName, 'date', formatDatetime(minVal), formatDatetime(maxVal))
        dailyData = dict.fromkeys(self.dbDailyHistoryHeader, 0)
        dailyData['date'] = formatDatetime(lastDay)
        numValues = dict.fromkeys(self.sensorTypes, 0)

        # Initialization of dailyData
        for column in dailyData:
            if 'MIN' in column:
                dailyData[column] = float('inf')
            elif 'MAX' in column:
                dailyData[column] = float('-inf')
            elif 'AVG' in column:
                dailyData[column] = 0.

        # Calculus of MIN, MAX and addition of all values to AVG
        for entry in data:
            for key,value in entry.items():
                if key != 'date' and value != None:
                    dailyData[key + 'MIN'] = min(dailyData[key + 'MIN'], value)
                    dailyData[key + 'MAX'] = max(dailyData[key + 'MAX'], value)
                    dailyData[key + 'AVG'] += value
                    numValues[key] += 1

        # Calculus of AVG
        for key in self.sensorTypes.keys():
            if numValues[key] != 0:
                dailyData[key + 'AVG'] = round(dailyData[key + 'AVG']/numValues[key],1)
            else:
                # there is no value registered for this sensor in 'lastDay'
                dailyData[key + 'AVG'] = None
                dailyData[key + 'MIN'] = None
                dailyData[key + 'MAX'] = None

        # Update daily history database.
        self.dbc.insert(self.dailyHistoryDataName, dailyData)

        # Change next update time
        nextUpdate = self.alarms.getNextUpdateStr('updateDailyHistory')
        self.dbc.update("nextUpdates", {"nextUpdate":nextUpdate}, "name", "dailyHistory")

        print('Inserted data to daily history')

    ###############
    # Run station #
    ###############

    def run(self):

        """
        This function starts the station, from this moment it will receive data from the Arduino and store
        it to the database.
        """

        while True:

            # Read data from Arduino and update the partial data
            data = self.ard.readInput()

            # Execute functions when it gets new data
            for (sensor,value) in data:
                if sensor in self.sensorNamesList:
                    valueType = self.sensorData[sensor]
                    for f in self.newValueFunctions:
                        f(valueType, value)
                    printSensor(sensor, value)

            # Execute functions when it is necessary
            toDo = self.alarms.getThingsToDo()
            for func in toDo:
                func()

            # Read from terminal
            inp = self.t.readLine()
            if inp != "":
                self.ard.write(inp)

            time.sleep(0.1)

def main():
    s = Station()
    s.run()

if __name__ == '__main__':
    s = Station()
    s.run()


