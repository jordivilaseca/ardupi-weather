from flask import Flask, render_template

import sys
import os
sys.path.append(os.path.abspath('..'))
from database import databaseController

import yaml
 
app = Flask(__name__)

global dbc
global databaseName

def getPath(path, fileName):
	return "/home/jordivilaseca/Documents/estacioMeteorologica/data/weatherStation"

def readConfiguration():
	with open("./../config.yml", 'r') as ymlfile:
		cfg = yaml.load(ymlfile)

	configureDatabase(cfg['database'])

def configureDatabase(database):
	dbc = databaseController.databaseController()
	databaseName = database['name']

	usedDatabase = database['used']
	db = database[usedDatabase]
	if usedDatabase == 'sqlite':
		dbc.enableSqlite(getPath(db['path'], databaseName))
	elif usedDatabase == 'mongo':
		dbc.enableMongo(databaseName, db['server'], db['port'])
	else:
		'Unknown database name'   
 
@app.route('/')
def home(chartID = 'chart_ID', chart_type = 'line', chart_height = 350):
	chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
	rangeSelector = {"selected": 1}
	series = [{"name": 'Label1', "data": [[i*i, i] for i in range(200)]}]
	title = {"text": 'My Title'}
	xAxis = {"categories": ['xAxis Data1']}
	yAxis = {"title": {"text": 'yAxis Label'}}
	return render_template('index.html', image_name='static/img/header.jpg', rangeSelector=rangeSelector, chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)
 
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, passthrough_errors=True)
	app.run(debug=True)

	readConfiguration()
