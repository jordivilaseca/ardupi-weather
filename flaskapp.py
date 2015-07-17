from flask import Flask, render_template

import json
import time
from threading import Thread, Event
from chartManager import chartManager
from config import cfg, templatesFlaskPath, staticFlaskPath, dataPath
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__,static_folder=staticFlaskPath,template_folder=templatesFlaskPath)
socketio = SocketIO(app)
thread = Thread()
thread_stop_event = Event()
connectedClients = 0

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def background_thread():
	uE = cfg['data']['history']['updateEvery']
	sleepTime = uE['d']*24*3600 + uE['h']*3600 + uE['m']*60 + uE['s']
	while not thread_stop_event.isSet():
		time.sleep(2)
		data = readJsonData(dataPath + 'history.json')
		socketio.emit('sample',data[-1],namespace='/test')

cm = chartManager()

@app.route('/')
def home():
	return render_template('index.html', image_name='static/img/header.jpg', chart=cm.getChart('history'))

@socketio.on('my event', namespace='/test')
def test_message(message):
	pass

@socketio.on('connect', namespace='/test')
def connect():
	global thread
	global connectedClients
	connectedClients += 1

	if not thread.isAlive():
		thread_stop_event.clear()
		thread = Thread(target=background_thread,name='flaskapp.py: SocketIO thread')
		thread.start()

@socketio.on('disconnect', namespace='/test')
def disconnect():
	global connectedClients
	connectedClients -= 1

	if connectedClients == 0:
		thread_stop_event.set()
 
if __name__ == '__main__':
	app.debug = True
	app.host = cfg['webserver']['host']
	app.port = cfg['webserver']['port']
	socketio.run(app)

