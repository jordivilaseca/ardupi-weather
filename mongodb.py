import pymongo


class mongodb():
	def __init__(self, server, port):
		self.server = server
		self.port = port

		try:
			self.client=pymongo.MongoClient(server,port)
			print ("Connected successfully!!!")
		except pymongo.errors.ConnectionFailure as e:
			print ("Could not connect to MongoDB: %s" % e)

	def __init__(self):
		self.server = 'localhost'
		self.port = 27017

		try:
			self.client=pymongo.MongoClient(self.server,self.port)
			print ("Connected successfully!!!")
		except pymongo.errors.ConnectionFailure as e:
			print ("Could not connect to MongoDB: %s" % e)

	def getCollection(self, dbName, dbCollection):
		return self.client[dbName][dbCollection]

	def insert(self, dbName, dbCollection, dic):
		coll = self.getCollection(dbName,dbCollection)
		coll.insert(dic)

	def queryOne(self, dbName, dbCollection, queryDic=None):
		coll = self.getCollection(dbName,dbCollection)
		return list(coll.find_one(queryDic))

	def query(self, dbName, dbCollection, queryDic=None):
		coll = self.getCollection(dbName,dbCollection)
		return list(coll.find(queryDic))

	def queryBetweenValues(self, dbName, dbCollection, attribute, minValue, maxValue):
		coll = self.getCollection(dbName,dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}))

	def queryBetweenValuesSortAsc(self,dbName,dbCollection,attribute,minValue,maxValue):
		coll = self.getCollection(dbName,dbCollection)
		return list(coll.find({attribute: {"$gte": minValue, "$lte": maxValue}}).sort([(attribute, pymongo.ASCENDING)]))

if __name__ == '__main__':
	db = mongodb()
	ret = db.queryBetweenValuesSortAsc('prova','prova1', 'pepe', 'aaaaa','ccccc')
	for elem in ret:
		print (elem)