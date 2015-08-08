from flask import Flask, render_template

import json
import time
from threading import Thread, Event
from chartManager import chartManager
from config import cfg, templatesFlaskPath, staticFlaskPath, dataPath
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
	data = readJsonData(dataPath + 'history.json')
	socketio.emit('historyUpdate',data[-1],namespace='/test')

def sendCurrentData():
	data = readJsonData(dataPath + 'currentData.json')
	socketio.emit('currentDataUpdate',data,namespace='/test')

functions = {'sendHistoryData': sendHistoryData, 'sendCurrentData': sendCurrentData}

def liveUpdatesThread():
	alarms = alarm()

	if cfg['webserver']['charts']['history']['enable']:
		update = cfg['data']['history']['updateEvery']
		alarms.add(sendHistoryData, update['d'], update['h'], update['m'], update['s'])

	if cfg['webserver']['liveData']['enable']:
		update = cfg['webserver']['liveData']['updateEvery']
		alarms.add(sendCurrentData, update['d'], update['h'], update['m'], update['s'])
	
	while not thread_stop_event.isSet():
		toDo = alarms.getThingsToDo()
		for func in toDo:
			func()
		time.sleep(5)

cm = chartManager()

@app.route('/')
def home():
	currentData = readJsonData(dataPath + 'currentData.json')
	return render_template('index.html', image_name='static/img/header.jpg', chart=cm.getChart('history'), currentData = currentData)

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

