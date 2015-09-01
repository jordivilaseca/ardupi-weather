#!/usr/bin/python

from config import cfg, DATA_PATH, LOG_PATH
from arduino.arduino import arduino
from database import databaseController
import os
from terminal import terminal
from alarm import alarm
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import json

LOG_FILE = LOG_PATH + 'station.log'
handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=6)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

logger = logging.getLogger('station')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def getDatetime():
    return int(datetime.datetime.utcnow().timestamp())*1000

def formatDatetime(date):
    return date.timestamp()*1000

def printSensor(sensor, value):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print (date, sensor, value)

class station:
    def __init__(self):
        self.dbc = databaseController.databaseController()
        self.newValueFunctions = []
        self.alarms = alarm()

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

        #configure station for webserver support
        webserverCfg = cfg['webserver']
        self.configureWebserverSupport(webserverCfg, historyCfg, dailyHistoryCfg)

        #Initialize terminal input
        self.t = terminal()

    #Configuration functions

    def configureArduino(self, ard):
        connection = ard['usedConnection']
        self.ard = arduino(connection, ard[connection], self.sensorUnits)

    def configureDatabase(self, data):
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
        self.dbc.createContainer('nextUpdates', {'name':'TEXT','nextUpdate':'TEXT'})
        self.dbc.deleteALL('nextUpdates')

    def initialitzeCurrentData(self, currentData):
        if currentData['enable']:
            self.currentDataDatabaseName = currentData['name']
            self.dbCurrentDataHeader = {'type':'TEXT', 'value': 'TEXT'}

            self.currentDataValues = {}

            self.dbc.createContainer(self.currentDataDatabaseName, self.dbCurrentDataHeader)

            # Remove all data from previous initializations
            self.dbc.deleteALL(self.currentDataDatabaseName)

            # Initialize current data database
            for key in self.sensorTypes.keys():
                self.dbc.insert(self.currentDataDatabaseName, {'type':key, 'value':None})

            # Add update current data alarm
            update = currentData['updateEvery']
            self.alarms.add('updateCurrentData', self.updateCurrentDataDatabase, update['d'], update['h'], update['m'], update['s'])

            # Insert next update to database
            self.dbc.insert('nextUpdates', {'name':'currentData','nextUpdate': self.alarms.getNextUpdateStr('updateCurrentData')})

            self.newValueFunctions.append(self.updateCurrentData)

    def initialitzeHistoryDatabase(self, history):
        if history['enable']:
            self.dbHistoryHeader = {'date' : 'TIMESTAMP'}
            self.dbHistoryHeader.update(self.sensorTypes)

            self.historyDataName = history['name']
            self.dbc.createContainer(self.historyDataName, self.dbHistoryHeader)

            self.sensorSum = dict.fromkeys(self.sensorTypes, 0)
            self.sensorNum = dict.fromkeys(self.sensorTypes, 0)

            update = history['updateEvery']
            self.alarms.add('updateHistory', self.updateHistoryDatabase, update['d'], update['h'], update['m'], update['s'])

            self.dbc.insert('nextUpdates', {'name':'history','nextUpdate': self.alarms.getNextUpdateStr('updateHistory')})

            self.newValueFunctions.append(self.updateHistoryData)

    def initializeDailyHistoryDatabase(self, daily, history):
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

            self.dbc.insert('nextUpdates', {'name':'dailyHistory','nextUpdate': self.alarms.getNextUpdateStr('updateDailyHistory')})

    def configureWebserverSupport(self, webserver, history, dailyHistory):
        if webserver['enable']:
            if not (history['enable'] and dailyHistory['enable']):
                print("webserver cannot be enabled because 'history' or 'dailyHistory' are not enabled")
                return

    #Functions to execute when a new sensor value arrives
    def updateCurrentData(self, valueType, value):
        self.currentDataValues[valueType] = value

    def updateHistoryData(self, valueType, value):
        self.sensorSum[valueType] += value
        self.sensorNum[valueType] += 1

    #Functions to execute at a determined time  

    def updateCurrentDataDatabase(self):
        for (key,value) in self.currentDataValues.items():
            self.dbc.update(self.currentDataDatabaseName,{"value":value}, "type", key)

        # Change next update time
        nextUpdate = self.alarms.getNextUpdateStr('updateCurrentData')
        self.dbc.update("nextUpdates", {"nextUpdate":nextUpdate}, "name", "currentData")

        print('Updated current data file')

    def updateHistoryDatabase(self):
        newValues = {'date' : getDatetime()}
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
        # Query to database
        lastDay = datetime.date.today() - datetime.timedelta(days=1)
        minVal = datetime.datetime.combine(lastDay, datetime.datetime.min.time())
        maxVal = datetime.datetime.combine(lastDay, datetime.datetime.max.time())
        data = self.dbc.queryBetweenValues(self.historyDataName, 'date', formatDatetime(minVal), formatDatetime(maxVal))
        dailyData = dict.fromkeys(self.dbDailyHistoryHeader, 0)
        dailyData['date'] = lastDay.strftime("%Y-%m-%d")
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

        self.dbc.insert(self.dailyHistoryDataName, dailyData)

        # Change next update time
        nextUpdate = self.alarms.getNextUpdateStr('updateDailyHistory')
        self.dbc.update("nextUpdates", {"nextUpdate":nextUpdate}, "name", "dailyHistory")

        print('Inserted data to daily history')

    def run(self):
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

if __name__ == '__main__':
    s = station()
    s.run()

        
