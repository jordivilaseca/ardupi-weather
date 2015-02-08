#!/usr/bin/python

import sqlite3

class database:
	def __init__(self, path):
		self.db = sqlite3.connect(path)
		self.cursor = self.db.cursor()

	def createTable(self, tableName, variables):
		sentence = "CREATE TABLE IF NOT EXISTS " + tableName + "(" + ", ".join(variables) + ")"
		self.cursor.execute(sentence)
		self.db.commit()

	def insert(self, tableName, variables, values):
		valuesArray = ["?"] * len(variables)
		sentence = "INSERT INTO " + tableName + "(" + ", ".join(variables) + ") VALUES(" + ", ".join(valuesArray) + ")"
		self.cursor.execute(sentence,tuple (values))
		self.db.commit()

	def close():
		self.db.close()
