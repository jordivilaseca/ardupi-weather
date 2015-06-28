import pymongo


class mongodb:
	def __init__(self, server, port, dbName):
		self.server = server
		self.port = port
		self.dbName = dbName

		try:
			self.client=pymongo.MongoClient(server,port)
			print ("Connected successfully!!!")
		except pymongo.errors.ConnectionFailure as e:
			print ("Could not connect to MongoDB: %s" % e)

	def getCollection(self, dbCollection):
		return self.client[self.dbName][dbCollection]

	def insert(self, dbCollection, dic):
		coll = self.getCollection(dbCollection)
		coll.insert(dic)

	def queryOne(self, dbCollection, queryDic=None):
		coll = self.getCollection(dbCollection)
		return list(coll.find_one(queryDic))

	def query(self, dbCollection, queryDic=None):
		coll = self.getCollection(dbCollection)
		return list(coll.find(queryDic))

	def queryBetweenValues(self, dbCollection, attribute, minValue, maxValue):
		coll = self.getCollection(dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}))

	def queryBetweenValuesSortAsc(self, dbCollection, attribute, minValue, maxValue):
		coll = self.getCollection(dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}).sort([(attribute, pymongo.ASCENDING)]))