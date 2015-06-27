from database import mongodb
from database import sqlitedb

class databaseController:
	def __init__(self):
		self.type = ''

	def enableSqlitedb(self,path):
		self.db = sqlitedb.sqlitedb(path)
		self.type = 'sqlite'

	def enableMongodb(self, dbName, server='localhost',port=27017):
		self.db = mongodb.mongodb(server,port)
		self.type = 'mongo'

	def createDataContainer(self, containerName, dataTitles):
		if self.type == 'sqlite':
			self.db.createTable(containerName, dataTitles)
		elif self.type == 'mongo':
			pass
		else:
			print('Unable to create a data container, there is no database enabled')

	def insertDataEntry(self, containerName, header, values):
		if self.type == 'sqlite':
			self.db.insert(containerName, header, values)
		elif self.type == 'mongo':
			self.db.insert(containerName, dict(zip(header, values)))
		else:
			print('Unable to insert data to a data container, there is no database enabled')
		