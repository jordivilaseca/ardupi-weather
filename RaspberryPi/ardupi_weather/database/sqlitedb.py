#!/usr/bin/python

import sqlite3

class SQLiteDB:

	"""
	Class dealing with the storing of the data to a sqlite database.
	"""

	def __init__(self, path):

		"""
		Initialization of a sqlite database.

		Args:
			path: path to the database, it must include the name of the database.
		"""

		self.path = path
		self.conn = sqlite3.connect(path)
		self.conn.row_factory = sqlite3.Row
		self.cursor = self.conn.cursor()

	def createTable(self, tableName, header):

		"""
		Function that creates a new table to the database, or does nothing in case this was previously created

		Args:
			tableName: Name of the table to create.
			header: A list, each entry contains the variable name and its type separated by a space.
		"""

		sentence = "CREATE TABLE IF NOT EXISTS " + tableName + "(" + ", ".join(header) + ")"
		self.cursor.execute(sentence)
		self.conn.commit()

	def insert(self, tableName, valuesDict):

		"""
		It Inserts a new entry to the database.

		Args:
			tableName: Name of the table to which the data will be inserted.
			valuesDict: Dictionary containing the variables and its values.
		"""

		header = list(valuesDict.keys())
		values = tuple(valuesDict.values())

		valuesArray = ["?"] * len(header)
		sentence = "INSERT INTO " + tableName + "(" + ", ".join(header) + ") VALUES(" + ", ".join(valuesArray) + ")"
		self.cursor.execute(sentence, values)
		self.conn.commit()

	def upsert(self, tableName, valuesDict):

		"""
		It inserts an entry if it does not exist, or updates it otherwise.

		The query key used to know if the entry was previously inserted is the primary key of the table.

		Args:
			tableName: Name of the table to which the data will be updated or inserted.
			valuesDict: Dictionary containing the variables names and its values.
		"""

		header = list(valuesDict.keys())
		values = tuple(valuesDict.values())

		valuesArray = ["?"] * len(header)
		sentence = "INSERT OR REPLACE INTO " + tableName + "(" + ", ".join(header) + ") VALUES(" + ", ".join(valuesArray) + ")"
		self.cursor.execute(sentence, values)
		self.conn.commit()

	def update(self, tableName, valuesDict, conditionKey, conditionValue):

		"""
		It updates an entry of the database if its conditionKey is equal to the conditionValue.

		Args:
			tableName: Name of the table.
			valuesDict: Dictionary containing the variables and their new values.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.
		"""

		header = list(valuesDict.keys())
		values = tuple(valuesDict.values())

		sentence = "UPDATE " + tableName + " SET " + ", ".join("{!s}=?".format(key) for key in header) + " WHERE " + conditionKey + " == " + "'" + conditionValue + "'"
		self.cursor.execute(sentence, values)
		self.conn.commit()

	def queryBetweenValues(self, tableName, attribute, minValue, maxValue):

		"""
		It searches for all the entries between the minValue and maxValue for the variable attribute.

		Args:
			tableName: Name of the table.
			attribute: Name of the variable to make the query.
			minValue: Minimum value for the attribute.
			maxValue: Maximum value for the attribute.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		sentence = "SELECT * FROM " + tableName + " WHERE " + attribute + " BETWEEN '" + minValue + "' AND '" + maxValue + "'"
		query = self.conn.execute(sentence)
		colname = [ d[0] for d in query.description ]
		return [ dict(zip(colname, r)) for r in query.fetchall() ]

	def queryOne(self, tableName, conditionKey, conditionValue):

		"""
		It searches for the first instance that achieves the condition.

		Args:
			tableName: Container name of the database.
			conditionKey: Variable to use as condition.
			conditionValue: Value of the conditionKey variable.

		Returns:
			Returns a dictionary with the name of the variable as a key and its value.
		"""

		sentence = "SELECT * FROM " + tableName + " WHERE " + conditionKey + "=='" + conditionValue +"'"
		query = self.conn.execute(sentence)
		return query.fetchone()

	def queryAll(self, tableName):

		"""
		It gets all the entries of a table.

		Args:
			tableName: Name of the table.

		Returns:
			Returns a list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		sentence = "SELECT * FROM " + tableName
		query = self.conn.execute(sentence)
		colname = [ d[0] for d in query.description ]
		return [dict(zip(colname, r)) for r in query.fetchall()]

	def querySortLimit(self, tableName, attribute, sortOrder, limit):

		"""
		It gets the first or last 'limit' entries of a collection.

		Args:
			tableName: Name of the table.
			attribute: Variable name that will be sorted.
			sortOrder: 1 is ascending order, -1 is descending order.
			limit: Number of entries to fetch. If it is 0 it will fetch all the entries.

		Returns:
			Returns an ordered list, where each position is an entry and contains a dictionary with the name of
			the variable as a key and its value.
		"""

		sortDesc = "DESC" if sortOrder == 1 else "ASC"
		limitSent = "" if limit == 0 else " LIMIT " + str(limit)
		sentence = "SELECT * FROM " + tableName + " ORDER BY " + attribute + " " + sortDesc + limitSent
		query = self.conn.execute(sentence)
		colname = [ d[0] for d in query.description ]
		return [dict(zip(colname, r)) for r in query.fetchall()]

	def deleteALL(self, tableName):

		"""
		It deletes all the entries of a table.

		Args:
			tableName: Name of the table.
		"""

		sentence = "DELETE FROM " + tableName
		self.cursor.execute(sentence)

	def close():

		"""
		It closes the connection to the database.
		"""
		self.conn.close()
