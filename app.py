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

def createChart(cfg):
	chart = {}
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

	chart['chart'] = {"height": 700}
	chart['chartID'] = 'chart_ID'
	chart['rangeSelector'] = {"selected": 1}
	chart['series'] = series
	chart['title'] = {"text": 'My Title'}
	chart['xAxis'] = {"categories": ['Time']}
	chart['yAxis'] = yAxis
	return chart

@app.route('/')
def home():
	cfg = readConfiguration()
	chart = createChart(cfg)
	return render_template('index.html', image_name='static/img/header.jpg', chart=chart)
 
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, passthrough_errors=True)
	app.run(debug=True)

	readConfiguration()
