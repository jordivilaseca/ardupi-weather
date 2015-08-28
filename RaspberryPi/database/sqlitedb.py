#!/usr/bin/python

import sqlite3

class sqlitedb:
	def __init__(self, path):
		self.path = path
		self.conn = sqlite3.connect(path)
		self.conn.row_factory = sqlite3.Row
		self.cursor = self.conn.cursor()

	def createTable(self, tableName, header):
		sentence = "CREATE TABLE IF NOT EXISTS " + tableName + "(" + ", ".join(header) + ")"
		self.cursor.execute(sentence)
		self.conn.commit()

	def insert(self, tableName, header, values):
		valuesArray = ["?"] * len(header)
		sentence = "INSERT INTO " + tableName + "(" + ", ".join(header) + ") VALUES(" + ", ".join(valuesArray) + ")"
		self.cursor.execute(sentence,tuple (values))
		self.conn.commit()

	def update(self, tableName, header, values, conditionKey, conditionValue):
		sentence = "UPDATE " + tableName + " SET " + ", ".join("{!s}=?".format(key) for key in header) + " WHERE " + conditionKey + " == " + "'" + conditionValue + "'"
		self.cursor.execute(sentence, tuple(values))
		self.conn.commit()

	def queryBetweenValues(self, tableName, attribute, minValue, maxValue):
		sentence = "SELECT * FROM " + tableName + " WHERE " + attribute + " BETWEEN '" + minValue + "' AND '" + maxValue + "'"
		query = self.conn.execute(sentence)
		colname = [ d[0] for d in query.description ]
		return [ dict(zip(colname, r)) for r in query.fetchall() ]

	def queryOne(self, queryCols, tableName, conditionKey, conditionValue):
		sentence = "SELECT (" + ", ".join(queryCols) + ") FROM " + tableName + " WHERE " + conditionKey + "=='" + conditionValue +"'"
		query = self.conn.execute(sentence)
		return query.fetchone()

	def queryAll(self, tableName):
		sentence = "SELECT * FROM " + tableName
		query = self.conn.execute(sentence)
		colname = [ d[0] for d in query.description ]
		return [dict(zip(colname, r)) for r in query.fetchall()]

	def deleteALL(self, tableName):
		sentence = "DELETE FROM " + tableName
		self.cursor.execute(sentence)

	def close():
		self.conn.close()
