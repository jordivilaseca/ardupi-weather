import pymongo


class mongodb:
	def __init__(self, server, port, dbName):
		self.server = server
		self.port = port
		self.dbName = dbName

		try:
			self.client=pymongo.MongoClient(server,port)
		except pymongo.errors.ConnectionFailure as e:
			print ("Could not connect to MongoDB: %s" % e)

	def getCollection(self, dbCollection):
		return self.client[self.dbName][dbCollection]

	def insert(self, dbCollection, dic):
		coll = self.getCollection(dbCollection)
		coll.insert(dic)

	def update(self, dbCollection, dic, conditionKey, conditionValue):
		coll = self.getCollection(dbCollection)
		coll.update({conditionKey: conditionValue}, {'$set': dic}, False)

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
		coll.remove()