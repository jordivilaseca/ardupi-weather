from database import mongodb
from database import sqlitedb

class databaseController:
	def __init__(self):
		self.type = ''

	def enableSqlite(self,path):
		self.db = sqlitedb.sqlitedb(path)
		self.type = 'sqlite'

	def enableMongo(self, dbName, server='localhost',port=27017):
		self.db = mongodb.mongodb(server, port, dbName)
		self.type = 'mongo'

	def createDataContainer(self, containerName, dataUnitsDic):
		if self.type == 'sqlite':
			header = [var + ' ' + vType for var, vType in dataUnitsDic.items()]
			self.db.createTable(containerName, header)
		elif self.type == 'mongo':
			pass
		else:
			print('Unable to create a data container, there is no database enabled')

	def insertDataEntry(self, containerName, valuesDict):
		if self.type == 'sqlite':
			self.db.insert(containerName, valuesDict.keys(), valuesDict.values())
		elif self.type == 'mongo':
			self.db.insert(containerName, valuesDict)
		else:
			print('Unable to insert data to a data container, there is no database enabled')

	def queryBetweenValues(self, containerName, attribute, minValue, maxValue):
		return self.db.queryBetweenValues(containerName, attribute, minValue, maxValue)

	def queryAll(self, containerName):
		return self.db.queryAll(containerName)
		