import pymongo
import json
import os
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('mongodb')

def jsonAdd(jsonFile, collection, func, newEntry=None):
	data = []
	with open(jsonFile, 'r') as f:
		data = json.loads(f.read())

	data.append({'coll':collection, 'data':newEntry, 'func': func})

	with open(jsonFile, 'w') as f:
		f.write(json.dumps(data))
	logger.warning('-ADDED TO QUEUE- (' + func + ' on ' + collection + ') ' + json.dumps(newEntry))

class mongodb:
	def __init__(self, dbName, uri, dataPath, logPath):
		self.uri = uri
		self.dbName = dbName

		logFile = logPath + 'mongodb.log'
		handler = TimedRotatingFileHandler(logFile, when="midnight", backupCount=6)
		handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))

		logger.setLevel(logging.INFO)
		logger.addHandler(handler)

		try:
			self.client=pymongo.MongoClient(uri)
		except pymongo.errors.ConnectionFailure as e:
			print ("Could not connect to MongoDB: %s" % e)

		self.jsonFile = dataPath + 'dataToUpdate.json'
		if not os.path.exists(self.jsonFile):
			with open(self.jsonFile, 'w+') as f:
				f.write('[]')
		self.existsDataToDump = self.dumpJson()

	def dumpJson(self):
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
					coll.upsert(entry['data'])

				del data[0]
				logger.info('-EXECUTED- ' + entry['func'] + ' on ' + entry['coll'] + ', tried at ' + entry['data']['date'])
			except pymongo.errors.ServerSelectionTimeoutError:
				timeoutError = True
				logger.warning('-ERROR DUMPING-' + entry['func'] + ' on ' + entry['coll'] + ', tried at ' + entry['data']['date'])
			i += 1

		with open(self.jsonFile, 'w') as f:
			f.write(json.dumps(data))

		return timeoutError


	def getCollection(self, dbCollection):
		return self.client[self.dbName][dbCollection]

	def insert(self, dbCollection, dic):
		coll = self.getCollection(dbCollection)
		try:
			coll.insert(dic)
		except pymongo.errors.ServerSelectionTimeoutError:
			jsonAdd(self.jsonFile, dbCollection, 'insert', dic)
			self.existsDataToDump = True
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def upsert(self, dbCollection, queryKey, dic):
		coll = self.getCollection(dbCollection)
		try:
			coll.update({queryKey:dic[queryKey]}, dic, upsert=True)
		except pymongo.errors.ServerSelectionTimeoutError:
			jsonAdd(self.jsonFile, dbCollection, 'upsert', dic)
			self.existsDataToDump = True
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def update(self, dbCollection, dic, conditionKey, conditionValue):
		coll = self.getCollection(dbCollection)
		try:
			coll.update({conditionKey: conditionValue}, {'$set': dic}, False)
		except pymongo.errors.ServerSelectionTimeoutError:
			pass
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()

	def queryOne(self, queryCols, dbCollection, conditionKey, conditionValue):
		coll = self.getCollection(dbCollection)

		queryFields = {key: True for key in queryCols}
		queryFields['_id'] = False

		return coll.find_one({conditionKey:conditionValue}, queryFields)

	def query(self, dbCollection, queryDic=None):
		coll = self.getCollection(dbCollection)
		return list(coll.find(queryDic))

	def queryAll(self, dbCollection):
		coll = self.getCollection(dbCollection)
		return list(coll.find(None, {'_id': False}))

	def queryBetweenValues(self, dbCollection, attribute, minValue, maxValue):
		coll = self.getCollection(dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}, {'_id': False}))

	def queryBetweenValuesSortAsc(self, dbCollection, attribute, minValue, maxValue):
		coll = self.getCollection(dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}).sort([(attribute, pymongo.ASCENDING)]))

	def deleteALL(self, dbCollection):
		coll = self.getCollection(dbCollection)
		try:
			coll.remove()
		except pymongo.errors.ServerSelectionTimeoutError:
			pass
		else:
			if self.existsDataToDump:
				self.existsDataToDump = self.dumpJson()
