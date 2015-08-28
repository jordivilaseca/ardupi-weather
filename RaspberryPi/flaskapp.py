from flask import Flask, render_template, send_from_directory, Response, safe_join

import json
import os.path
import time
import datetime
from threading import Thread, Event
from chartManager import chartManager
from config import cfg, TEMPLATES_FLASK_PATH, STATIC_FLASK_PATH, DATA_PATH, LOG_PATH
from flask.ext.socketio import SocketIO, emit
from alarm import alarm
from WebserverDataUpdater import WebserverDataUpdater

import logging


logging.basicConfig(level=logging.INFO)

app = Flask(__name__,static_folder=STATIC_FLASK_PATH,template_folder=TEMPLATES_FLASK_PATH)
socketio = SocketIO(app)

socketThread = Thread()
thread_stop_event = Event()
connectedClients = 0

WDUthread = WebserverDataUpdater()
WDUthread.start()

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def sendHistoryData():
	global alarms
	data = readJsonData(DATA_PATH + 'history.json')
	socketio.emit('historyUpdate',data['data'][-1],namespace='/test')

	offset = cfg['webserver']['updateOffset']
	nextUpdate = datetime.datetime.strptime(data['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
	alarms.addOneTime('sendHistoryData', sendHistoryData, nextUpdate + datetime.timedelta(seconds=offset))

def sendCurrentData():
	global alarms
	data = readJsonData(DATA_PATH + 'currentData.json')
	socketio.emit('currentDataUpdate',data['data'],namespace='/test')

	offset = cfg['webserver']['updateOffset']
	nextUpdate = datetime.datetime.strptime(data['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
	alarms.addOneTime('sendCurrentData', sendCurrentData, nextUpdate + datetime.timedelta(seconds=offset))

alarms = None

def liveUpdatesThread():
	global alarms
	alarms = alarm()
	offset = cfg['webserver']['updateOffset']

	if cfg['webserver']['charts']['history']['enable']:
		nextUpdateStr = readJsonData(DATA_PATH + 'history.json')['nextUpdate']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr, "%Y-%m-%d %H:%M:%S.%f")
		alarms.addOneTime('sendHistoryData', sendHistoryData, nextUpdate + datetime.timedelta(seconds=offset))

	if cfg['webserver']['liveData']['enable']:
		nextUpdateStr = readJsonData(DATA_PATH + 'currentData.json')['nextUpdate']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr, "%Y-%m-%d %H:%M:%S.%f")
		alarms.addOneTime('sendCurrentData', sendCurrentData, nextUpdate + datetime.timedelta(seconds=offset))
	
	while not thread_stop_event.isSet():
		toDo = alarms.getThingsToDo()
		for func in toDo:
			func()
		time.sleep(5)

	del alarms

cm = chartManager()

@app.route('/')
def home():
	liveData = {}
	liveData['data'] = readJsonData(DATA_PATH + 'currentData.json')['data']
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

	image_name = 'css/background.JPG'
	return render_template('index.html', image_name=image_name, webpageTitle=webpageTitle, webpageSubtitle = webpageSubtitle, historyChart= historyChart, historyEnable = historyEnable, liveData = liveData, liveDataEnable = liveDataEnable, dailyHistoryChart = dailyHistoryChart, dailyHistoryEnable = dailyHistoryEnable)

@app.route('/log/<name>')
def log(name):
	filePath = safe_join(LOG_PATH, name)
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='text/plain')
	else:
		return "File not found"

@app.route('/data/<name>.json')
def data(name):
	filePath = safe_join(DATA_PATH, name + '.json')
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='application/json')
	return (name)

@app.route('/database')
def send_database():
	if cfg['data']['usedDB'] == 'sqlite':
		return send_from_directory(DATA_PATH, cfg['data']['name'])
	else:
		return ""

@socketio.on('connect', namespace='/test')
def connect():
	global socketThread
	global connectedClients
	connectedClients += 1

	if not socketThread.isAlive():
		thread_stop_event.clear()
		socketThread = Thread(target=liveUpdatesThread,name='flaskapp.py: SocketIO thread')
		socketThread.start()

@socketio.on('disconnect', namespace='/test')
def disconnect():
	global connectedClients
	connectedClients -= 1

	if connectedClients == 0:
		thread_stop_event.set()
 
if __name__ == '__main__':
	socketio.run(app, host=cfg['webserver']['host'],port=cfg['webserver']['port'])

