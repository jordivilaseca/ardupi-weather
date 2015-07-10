from flask import Flask, render_template

import sys
import os
import yaml
import json
 
app = Flask(__name__)

def getPath(fileName):
	return "/home/jordivilaseca/Documents/estacioMeteorologica/data/" + fileName

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def readConfiguration():
	with open("./../config.yml", 'r') as ymlfile:
		ymlData = yaml.load(ymlfile)
		cfg = dict(ymlData['webserver'])
	return dict(cfg)

def createChart():
	pass

@app.route('/')
def home(chartID = 'chart_ID', chart_height = 700):
	cfg = readConfiguration()
	chart = {"height": chart_height}
	rangeSelector = {"selected": 1}
	series = []
	yAxis = []
	panels = cfg['charts']['history']['panels']
	height = 100/len(panels)
	top = 0
	axisNum = 0
	for panel in panels:
		for f in panel['values']:
			data = readJsonData(getPath(f) + '.json')
			series.append({'type':panel['type'],'name':f,'data': data, 'yAxis': axisNum})
		yAxis.append({'title': {'text': panel['name']}, 'height': str(height)+'%', 'top': str(top)+'%', 'offset': 0, 'labels': {'align': 'right', 'x': -3}})
		top += height
		axisNum += 1
	title = {"text": 'My Title'}
	xAxis = {"categories": ['Time']}
	return render_template('index.html', image_name='static/img/header.jpg', rangeSelector=rangeSelector, chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)
 
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, passthrough_errors=True)
	app.run(debug=True)

	readConfiguration()
