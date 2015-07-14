from flask import Flask, render_template

import json
import time
from threading import Thread
from chartManager import chartManager
from config import cfg, templatesFlaskPath, staticFlaskPath, dataPath
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__,static_folder=staticFlaskPath,template_folder=templatesFlaskPath)
socketio = SocketIO(app)
thread = None

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def background_thread():
	"""Example of how to send server generated events to clients."""
	uE = cfg['database']['historyDB']['updateEvery']
	sleepTime = uE['d']*24*3600 + uE['h']*3600 + uE['m']*60 + uE['s']
	while True:
		time.sleep(sleepTime)
		data = readJsonData(dataPath + 'history.json')
		socketio.emit('sample',data[-1],namespace='/test')

cm = chartManager()

@app.route('/')
def home():
	global thread
	if thread is None:
		thread = Thread(target=background_thread)
		thread.start()
	return render_template('index.html', image_name='static/img/header.jpg', chart=cm.getChart('history'))

@socketio.on('my event', namespace='/test')
def test_message(message):
	pass
 
if __name__ == '__main__':
	app.debug = True
	app.host = cfg['webserver']['host']
	app.port = cfg['webserver']['port']
	socketio.run(app)

