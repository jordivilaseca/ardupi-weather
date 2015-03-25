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

if __name__ == '__main__':
	db = mongodb()
	print(db.client.database_names())