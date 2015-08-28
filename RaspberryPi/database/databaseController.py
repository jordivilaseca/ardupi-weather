class databaseController:
	def __init__(self):
		self.type = ''

	def enableSqlite(self,path):
		from database import sqlitedb

		self.db = sqlitedb.sqlitedb(path)
		self.type = 'sqlite'

	def enableMongo(self, dbName, server='localhost',port=27017):
		from database import mongodb
		
		self.db = mongodb.mongodb(server, port, dbName)
		self.type = 'mongo'

	def createContainer(self, containerName, dataUnitsDic):
		if self.type == 'sqlite':
			header = [var + ' ' + vType for var, vType in dataUnitsDic.items()]
			self.db.createTable(containerName, header)
		elif self.type == 'mongo':
			pass
		else:
			print('Unable to create a data container, there is no database enabled')

	def insert(self, containerName, valuesDict):
		if self.type == 'sqlite':
			self.db.insert(containerName, valuesDict.keys(), valuesDict.values())
		elif self.type == 'mongo':
			self.db.insert(containerName, valuesDict)
		else:
			print('Unable to insert data to a data container, there is no database enabled')

	def update(self, containerName, changesDict, conditionKey, conditionValue):
		if self.type == 'sqlite':
			self.db.update(containerName, changesDict.keys(),changesDict.values(), conditionKey, conditionValue)
		elif self.type == 'mongo':
			self.db.update(containerName, changesDict, conditionKey, conditionValue)
		else:
			print('Unable to update data, there is no database enabled')

	def deleteALL(self, containerName):
		if self.type == 'sqlite' or self.type == 'mongo':
			self.db.deleteALL(containerName)
		else:
			print('Unable to remove all data, there is no database enabled')

	def queryOne(self, queryCols, containerName, conditionKey, conditionValue):
		if self.type == 'sqlite' or self.type == 'mongo':
			return self.db.queryOne(queryCols, containerName, conditionKey, conditionValue)
		else:
			print('Unable to query Data, the is no database enabled')

	def queryBetweenValues(self, containerName, attribute, minValue, maxValue):
		return self.db.queryBetweenValues(containerName, attribute, minValue, maxValue)

	def queryAll(self, containerName):
		return self.db.queryAll(containerName)
		