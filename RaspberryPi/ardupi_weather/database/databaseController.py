#!/usr/bin/env python3

class DatabaseController:

	"""
	Class dealing with the storing of the data.

	It provides an interface to work with data with different databases, mongo and sqlite currently.
	"""

	def __init__(self):

		"""
		Initialize databaseController
		"""

		self.type = ''

	def enableSqlite(self,path):

		"""
		It enables the use of a sqlite database.

		Args:
			path: The path (including the file name) of the database file.
		"""

		from ardupi_weather.database.sqlitedb import SQLiteDB

		self.db = SQLiteDB(path)
		self.type = 'sqlite'

	def enableMongo(self, dbName, uri, dataPath, logPath):

		"""
		It enables the use of a mongo database.

		Args:
			dbName: The name of the database.
			uri: mongo connexion uri.
			dataPath: Path to the folder used as data folder.
			logPath: Path to the folder used as log folder.
		"""

		from ardupi_weather.database.mongodb import MongoDB

		self.db = MongoDB(dbName, uri, dataPath, logPath)
		self.type = 'mongo'

	def createContainer(self, containerName, dataUnitsDic):

		"""
		It creates a container to the database.

		It is equivalent to a table in a sqlite database or a collection in a mongo database.

		Args:
			containerName: The name of the container.
			dataUnitsDic: Variables that yo want to store and its type (INTEGER or FLOAT).
		"""

		if self.type == 'sqlite':
			header = [var + ' ' + vType for var, vType in dataUnitsDic.items()]
			self.db.createTable(containerName, header)
		elif self.type == 'mongo':
			pass
		else:
			raise Exception('Unable to create a data container, there is no database enabled')

	def insert(self, containerName, valuesDict):

		"""
		Insert a new entry to the database.

		Args:
			containerName: Container to which the data will be inserted.
			valuesDict: Dictionary containing the variables and its values.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			self.db.insert(containerName, valuesDict)
		else:
			raise Exception('Unable to insert data to a data container, there is no database enabled')

	def upsert(self, containerName, queryKey, valuesDict):

		"""
		It inserts an entry if it does not exist, or updates it otherwise.

		Args:
			containerName: Container to which the data will be updated or inserted.
			queryKey: Name of the variable that will be used to know if the data has to be inserted
				or updated.
			valuesDict: Dictionary containing the variables names and its values.
		"""

		if self.type == 'sqlite':
			# In this case, the queryKey is the primary key of the table, so it is not needed to pass its name.
			self.db.upsert(containerName, valuesDict)
		elif self.type == 'mongo':
			self.db.upsert(containerName, queryKey, valuesDict)
		else:
			raise Exception('Unable to insert data to data container, there is no database enabled')

	def update(self, containerName, changesDict, conditionKey, conditionValue):

		"""
		It updates an entry of the database if its conditionKey is equal to the conditionValue.

		Args:
			containerName: Container name of the database.
			changesDict: Dictionary containing the variables and their new values.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			self.db.update(containerName, changesDict, conditionKey, conditionValue)
		else:
			raise Exception('Unable to update data, there is no database enabled')

	def deleteALL(self, containerName):

		"""
		It deletes all the entries of a container.

		Args:
			containerName: Container name of the database.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			self.db.deleteALL(containerName)
		else:
			raise Exception('Unable to remove all data, there is no database enabled')

	def queryOne(self, containerName, conditionKey, conditionValue):

		"""
		It searches for the first instance that achieves the condition.

		Args:
			containerName: Container name of the database.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.

		Returns:
			Returns a dictionary with the name of the variable as a key and its value.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			return self.db.queryOne(containerName, conditionKey, conditionValue)
		else:
			raise Exception('Unable to query data, the is no database enabled')

	def queryBetweenValues(self, containerName, attribute, minValue, maxValue):

		"""
		It searches for all the entries between the minValue and maxValue for the variable attribute.

		Args:
			containerName: Container name of the database.
			attribute: Name of the variable to make the query.
			minValue: Minimum value for the attribute.
			maxValue: Maximum value for the attribute.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			return self.db.queryBetweenValues(containerName, attribute, minValue, maxValue)
		else:
			raise Exception('Unable to query data, the is no database enabled')

	def queryAll(self, containerName):

		"""
		It gets all the entries of a container

		Args:
			containerName: Container name of the database.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			return self.db.queryAll(containerName)
		else:
			raise Exception('Unable to query data, the is no database enabled')

	def querySortLimit(self, containerName, attribute, sortOrder, limit):

		"""
		It gets the first or last 'limit' entries of a collection.

		Args:
			containerName: Container name of the database.
			attribute: Variable name that will be sorted.
			sortOrder: 1 is ascending order, -1 is descending order.
			limit: Number of entries to fetch. If it is 0 it will fetch all the entries.

		Returns:
			Returns an ordered list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		if self.type == 'sqlite' or self.type == 'mongo':
			return self.db.querySortLimit(containerName, attribute, sortOrder, limit)
		else:
			raise Exception('Unable to query data, the is no database enabled')

