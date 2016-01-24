from flask import Flask, render_template, send_from_directory, Response, safe_join, request

import json
import os.path
import time
import datetime
from threading import Thread, Event
from chartManager import chartManager
from config import cfg, TEMPLATES_FLASK_PATH, STATIC_FLASK_PATH, DATA_PATH, LOG_PATH
from DataParser import DataParser

import logging


logging.basicConfig(level=logging.INFO)

app = Flask(__name__,static_folder=STATIC_FLASK_PATH,template_folder=TEMPLATES_FLASK_PATH)

dp = DataParser()

cm = chartManager()

@app.route('/')
def home():
	liveData = {}
	liveData['name'] = cfg['webserver']['liveData']['name']
	liveData['sensorNames'] = cfg['webserver']['names']['sensors']
	liveData['header'] = {'type': cfg['webserver']['names']['type'], 'value': cfg['webserver']['names']['value']}

	historyEnable = cfg['webserver']['charts']['history']['enable']
	dailyHistoryEnable = cfg['webserver']['charts']['dailyHistory']['enable']
	liveDataEnable = cfg['webserver']['liveData']['enable']

	historyChart = cm.getChart('history')
	dailyHistoryChart = cm.getChart('dailyHistory')

	webpageTitle = cfg['webserver']['title']
	webpageSubtitle = cfg['webserver']['subtitle']

	return render_template('index.html', webpageTitle=webpageTitle, webpageSubtitle = webpageSubtitle, historyChart= historyChart, historyEnable = historyEnable, liveData = liveData, liveDataEnable = liveDataEnable, dailyHistoryChart = dailyHistoryChart, dailyHistoryEnable = dailyHistoryEnable)

@app.route('/log/<name>')
def log(name):
	filePath = safe_join(LOG_PATH, name)
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='text/plain')
	else:
		return "File not found"

@app.route('/data')
def data():
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
	if cfg['data']['usedDB'] == 'sqlite':
		return send_from_directory(DATA_PATH, cfg['data']['name'])
	else:
		return ""
 
if __name__ == '__main__':
	app.run(host=cfg['webserver']['host'],port=cfg['webserver']['port'])

