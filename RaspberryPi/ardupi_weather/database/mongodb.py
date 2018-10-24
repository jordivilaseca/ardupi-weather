import pymongo
import json
import os
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('mongodb')

def jsonAdd(jsonFile, collection, func, newEntry, params=None):

	"""
	It appends a data entry to a json file.

	Args:
		jsonFile: Aboslut path to the json file.
		collection: Name of the collection to which the data has to be stored.
		func: Name of the operation to do (insert or upsert).
		newEntry: Dictionary containg the data to store.
		params: Extra parameters (a query key for a upsert operation).
	"""

	data = []
	with open(jsonFile, 'r') as f:
		data = json.loads(f.read())

	data.append({'coll':collection, 'data':newEntry, 'func': func, 'params': params})

	with open(jsonFile, 'w') as f:
		f.write(json.dumps(data))
	logger.warning('-ADDED TO QUEUE- (' + func + ' on ' + collection + ') ' + json.dumps(newEntry))

class MongoDB:

	"""
	Class dealing with the storing of the data to a mongo database.

	This class stores the data to a mongo database, in case that an exception occurs (for example, due to t
	timeout or connection problems), it stores the data to a intermediate file and the next time that a query
	to the database is correctly done it dumps the file to the database. The system stores operations as
	inserting or upserting an entry to the database.
	"""

	def __init__(self, dbName, uri, dataPath, logPath):

		"""
		Initialization of a database.

		Args:
			dbName: Name of the database.
			uri: Database connection uri.
			dataPath: Path to where auxiliary file will be created.
			logPath: Path to where log files will be created.
		"""
		self.uri = uri
		self.dbName = dbName

		logFile = logPath + 'mongodb.log'
		handler = TimedRotatingFileHandler(logFile, when="midnight", backupCount=6)
		handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

		logger.setLevel(logging.INFO)
		logger.addHandler(handler)

		try:
			self.client=pymongo.MongoClient(uri)
		except Exception as e:
			print ("Could not connect to MongoDB: %s" % e)

		self.jsonFile = dataPath + 'dataToUpdate.json'
		if not os.path.exists(self.jsonFile):
			with open(self.jsonFile, 'w+') as f:
				f.write('[]')
		self.existsDataToDump = self.dumpJson()

	def dumpJson(self):

		"""
		Function in charge of dumping the auxiliary json file to the database.

		In case that a mongo database error occurs during the dumping operation, the operation is aborted
		and the remaining operations to do to the database are updated.

		Returns:
			It returns if a database occurred during the dumping.
		"""
		data = []
		with open(self.jsonFile, 'r') as f:
			data = json.loads(f.read())

		timeoutError = False
		iMax = len(data)
		i = 0
		while not timeoutError and i < iMax:
			entry = data[0]
			coll = self.getCollection(entry['coll'])
			try:
				if entry['func'] == 'insert':
					coll.insert(entry['data'])
				elif entry['func'] == 'upsert':
					queryKey = entry['params']['queryKey']
					coll.update({queryKey:entry['data'][queryKey]}, entry['data'], upsert=True)

				del data[0]
				logger.info('-EXECUTED- ' + entry['func'] + ' on ' + entry['coll'])
			except Exception:
				timeoutError = True
				logger.warning('-ERROR DUMPING-' + entry['func'] + ' on ' + entry['coll'])
			i += 1

		with open(self.jsonFile, 'w') as f:
			f.write(json.dumps(data))

		return timeoutError


	def getCollection(self, dbCollection):

		"""
		It gets a collection object from the database.

		Args:
			dbCollection: Name of the collection.

		Returns:
			The collection object.
		"""
		return self.client[self.dbName][dbCollection]

	def insert(self, dbCollection, dic):

		"""
		It inserts a new document to a collection.

		In case a database error occurs during the operation, the data is stored and the operation
		done the next time a database operation is successfully done.

		Args:
			dbCollection: Name of the collection to which the data will be inserted.
			dic: Dictionary containing the variables and its values.
		"""

		coll = self.getCollection(dbCollection)
		try:
			coll.insert(dic)
		except Exception:
			jsonAdd(self.jsonFile, dbCollection, 'insert', dic)
			self.existsDataToDump = True
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def upsert(self, dbCollection, queryKey, dic):

		"""
		It inserts an entry if it does not exist, or updates it otherwise.

		In case a database error occurs during the operation, the data is stored and the operation
		done the next time a database operation is successfully done.

		Args:
			dbCollection: Collection to which the data will be updated or inserted.
			queryKey: Name of the variable that will be used to know if the data has to be inserted
				or updated.
			dic: Dictionary containing the variables names and its values.
		"""

		coll = self.getCollection(dbCollection)
		try:
			coll.update({queryKey:dic[queryKey]}, dic, upsert=True)
		except Exception:
			jsonAdd(self.jsonFile, dbCollection, 'upsert', dic, params={'queryKey': queryKey})
			self.existsDataToDump = True
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def update(self, dbCollection, dic, conditionKey, conditionValue):

		"""
		It updates an entry of the database if its conditionKey is equal to the conditionValue.

		Args:
			dbCollection: Collection name.
			dic: Dictionary containing the variables and their new values.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.
		"""

		coll = self.getCollection(dbCollection)
		try:
			coll.update({conditionKey: conditionValue}, {'$set': dic}, False)
		except Exception:
			pass
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def queryOne(self, dbCollection, conditionKey, conditionValue):

		"""
		It searches for the first instance that achieves the condition.

		Args:
			dbCollection: Container name of the database.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.

		Returns:
			Returns a dictionary with the name of the variable as a key and its value.
		"""

		coll = self.getCollection(dbCollection)

		return coll.find_one({conditionKey:conditionValue}, {'_id': False})

	def queryAll(self, dbCollection):

		"""
		It gets all the entries of a collection.

		Args:
			dbCollection: Collection name.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		coll = self.getCollection(dbCollection)
		return list(coll.find(None, {'_id': False}))

	def querySortLimit(self, dbCollection, attribute, sortOrder, limit):

		"""
		It gets the first or last 'limit' entries of a collection.

		Args:
			dbCollection: Collection name.
			attribute: Variable name that will be sorted.
			sortOrder: 1 is ascending order, -1 is descending order.
			limit: Number of entries to fetch. If it is 0 it will fetch all the entries.

		Returns:
			Returns an ordered list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		coll = self.getCollection(dbCollection)
		return coll.find(None, {'_id': False}).sort([(attribute, sortOrder)]).limit(limit)

	def queryBetweenValues(self, dbCollection, attribute, minValue, maxValue):

		"""
		It searches for all the entries between the minValue and maxValue for the variable attribute.

		Args:
			dbCollection: Collection name.
			attribute: Name of the variable to make the query.
			minValue: Minimum value for the attribute.
			maxValue: Maximum value for the attribute.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		coll = self.getCollection(dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}, {'_id': False}))

	def deleteALL(self, dbCollection):

		"""
		It deletes all the entries of a collection.

		Args:
			dbCollection: Collection name.
		"""

		coll = self.getCollection(dbCollection)
		try:
			coll.remove()
		except Exception:
			pass
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()
