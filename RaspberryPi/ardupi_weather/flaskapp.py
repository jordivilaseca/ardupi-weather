#!/usr/bin/env python3

from flask import Flask, render_template, send_from_directory, Response, safe_join, request

import json
import os.path
import time
import datetime
import logging
from ardupi_weather.config import cfg, TEMPLATES_FLASK_PATH, STATIC_FLASK_PATH, DATA_PATH, LOG_PATH
from ardupi_weather.flaskfiles.app.chartManager import ChartManager
from ardupi_weather.flaskfiles.app.dataParser import DataParser

# Set the logging level
logging.basicConfig(level=logging.INFO)

# Configure the flask app with the correct paths for the static files and the templates.
app = Flask(__name__,static_folder=STATIC_FLASK_PATH,template_folder=TEMPLATES_FLASK_PATH)

dp = DataParser()
cm = ChartManager()

@app.route('/')
def home():

	"""
	It loads the root webpage of the server.
	"""

	# Load all the variables related with the live data.
	liveData = {}
	liveData['name'] = cfg['webserver']['liveData']['name']
	liveData['sensorNames'] = cfg['webserver']['names']['sensors']
	liveData['header'] = {'type': cfg['webserver']['names']['type'], 'value': cfg['webserver']['names']['value']}

	# Load the configuration of the history chart.
	historyEnable = cfg['webserver']['charts']['history']['enable']
	dailyHistoryEnable = cfg['webserver']['charts']['dailyHistory']['enable']
	liveDataEnable = cfg['webserver']['liveData']['enable']

	# Load the configuration of the daily history chart.
	historyChart = cm.getChart('history')
	dailyHistoryChart = cm.getChart('dailyHistory')

	webpageTitle = cfg['webserver']['title']
	webpageSubtitle = cfg['webserver']['subtitle']

	return render_template('index.html', webpageTitle=webpageTitle, webpageSubtitle = webpageSubtitle, historyChart= historyChart, historyEnable = historyEnable, liveData = liveData, liveDataEnable = liveDataEnable, dailyHistoryChart = dailyHistoryChart, dailyHistoryEnable = dailyHistoryEnable)

@app.route('/log/<name>')
def log(name):

	"""
	It shows all the log files of the station. In case the webserver is running in the same computer as the
	station, its log files can be seen as well.
	"""

	filePath = safe_join(LOG_PATH, name)
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='text/plain')
	else:
		return "File not found"

@app.route('/data')
def data():

	"""
	It deals with the data requests, it makes a query to the database and returns the results.
	"""

	name = request.args.get('name')
	limit = request.args.get('limit')
	if limit == None or limit == 'full':
		limit = 0
		sortOrder = 1
	elif limit == 'last':
		limit = 1
		sortOrder = -1

	data = None
	if name == 'currentData':
		data = dp.currentDataStr()
	elif name == 'history':
		data = dp.historyStr(sortOrder, limit)
	elif name == 'dailyHistory':
		data = dp.dailyHistoryStr(sortOrder, limit)

	return Response(data, mimetype='application/json')


@app.route('/database')
def send_database():

	"""
	In the case of using a sqlite database, you can obtain a copy of the database.
	"""

	if cfg['data']['usedDB'] == 'sqlite':
		return send_from_directory(DATA_PATH, cfg['data']['name'])
	else:
		return ""

def main():
	app.run(host=cfg['webserver']['host'],port=cfg['webserver']['port'])

if __name__ == '__main__':
	main()

