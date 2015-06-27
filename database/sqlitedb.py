#!/usr/bin/python

import sqlite3

class sqlitedb:
	def __init__(self, path):
		self.db = sqlite3.connect(path, check_same_thread=False)
		self.cursor = self.db.cursor()

	def createTable(self, tableName, header):
		sentence = "CREATE TABLE IF NOT EXISTS " + tableName + "(" + ", ".join(header) + ")"
		self.cursor.execute(sentence)
		self.db.commit()

	def insert(self, tableName, header, values):
		valuesArray = ["?"] * len(header)
		sentence = "INSERT INTO " + tableName + "(" + ", ".join(header) + ") VALUES(" + ", ".join(valuesArray) + ")"
		self.cursor.execute(sentence,tuple (values))
		self.db.commit()

	def close():
		self.db.close()
