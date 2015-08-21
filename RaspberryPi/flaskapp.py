from flask import Flask, render_template, send_from_directory, Response, safe_join

import json
import os.path
import time
import datetime
from threading import Thread, Event
from chartManager import chartManager
from config import cfg, templatesFlaskPath, staticFlaskPath, dataPath, logPath
from flask.ext.socketio import SocketIO, emit
from alarm import alarm
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__,static_folder=staticFlaskPath,template_folder=templatesFlaskPath)
socketio = SocketIO(app)
thread = Thread()
thread_stop_event = Event()
connectedClients = 0

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def sendHistoryData():
	global alarms
	data = readJsonData(dataPath + 'history.json')
	socketio.emit('historyUpdate',data['data'][-1],namespace='/test')

	offset = cfg['webserver']['updateOffset']
	nextUpdate = datetime.datetime.strptime(data['nextUpdate'], "%Y-%m-%d %H:%M:%S.%f")
	alarms.addOneTime('sendHistoryData', sendHistoryData, nextUpdate + datetime.timedelta(seconds=offset))

def sendCurrentData():
	global alarms
	data = readJsonData(dataPath + 'currentData.json')
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
		nextUpdateStr = readJsonData(dataPath + 'history.json')['nextUpdate']
		nextUpdate = datetime.datetime.strptime(nextUpdateStr, "%Y-%m-%d %H:%M:%S.%f")
		alarms.addOneTime('sendHistoryData', sendHistoryData, nextUpdate + datetime.timedelta(seconds=offset))

	if cfg['webserver']['liveData']['enable']:
		nextUpdateStr = readJsonData(dataPath + 'currentData.json')['nextUpdate']
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
	liveData = readJsonData(dataPath + 'currentData.json')['data']
	numPills = 0
	historyEnable = cfg['webserver']['charts']['history']['enable']
	if historyEnable:
		numPills += 1
	dailyHistoryEnable = cfg['webserver']['charts']['dailyHistory']['enable']
	if dailyHistoryEnable:
		numPills += 1
	liveDataEnable = cfg['webserver']['liveData']['enable']
	if liveDataEnable:
		numPills += 1
	return render_template('index.html', image_name='static/img/header.jpg', historyChart=cm.getChart('history'), historyEnable = historyEnable, liveData = liveData, liveDataEnable = liveDataEnable, dailyHistoryChart = cm.getChart('dailyHistory'), dailyHistoryEnable = dailyHistoryEnable, numPills = numPills)

@app.route('/log/<name>')
def log(name):
	filePath = safe_join(logPath, name)
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='text/plain')
	else:
		return "File not found"

@app.route('/data/<name>.json')
def data(name):
	filePath = safe_join(dataPath, name + '.json')
	if os.path.isfile(filePath):
		with open(filePath, 'r') as f:
			data = f.read()
		return Response(data, mimetype='application/json')
	return (name)

@app.route('/database')
def send_database():
	if cfg['data']['usedDB'] == 'sqlite':
		return send_from_directory(dataPath, cfg['data']['name'])
	else:
		return ""

@socketio.on('connect', namespace='/test')
def connect():
	global thread
	global connectedClients
	connectedClients += 1

	if not thread.isAlive():
		thread_stop_event.clear()
		thread = Thread(target=liveUpdatesThread,name='flaskapp.py: SocketIO thread')
		thread.start()

@socketio.on('disconnect', namespace='/test')
def disconnect():
	global connectedClients
	connectedClients -= 1

	if connectedClients == 0:
		thread_stop_event.set()
 
if __name__ == '__main__':
	app.debug = True
	socketio.run(app, host=cfg['webserver']['host'],port=cfg['webserver']['port'])

