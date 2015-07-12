from flask import Flask, render_template

import sys
import os
import json
from config import cfg, dataPath, templatesFlaskPath, staticFlaskPath

app = Flask(__name__,static_folder=staticFlaskPath,template_folder=templatesFlaskPath)

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def createChart():
	chart = {}
	series = []
	yAxis = []
	panels = cfg['webserver']['charts']['history']['panels']
	top = 0
	axisNum = 0
	for panel in panels:
		for f in panel['values']:
			data = readJsonData(dataPath + f + '.json')
			tooltip = {'valueSuffix' : ' ' + panel['units']}
			series.append({'type':panel['type'],'name':f,'data': data, 'yAxis': axisNum, 'tooltip' : tooltip})
		yAxis.append({'title': {'text': panel['name']}, 'height': str(panel['height'])+'%', 'top': str(top)+'%', 'offset': 0, 'labels': {'align': 'right', 'x': -3}})
		top += panel['height'] + panel['offset']
		axisNum += 1

	chart['chart'] = {"height": cfg['webserver']['charts']['history']['height']}
	chart['chartID'] = 'chart_ID'
	chart['rangeSelector'] = {"selected": 1}
	chart['series'] = series
	chart['title'] = {"text": 'My Title'}
	chart['xAxis'] = {"categories": ['Time']}
	chart['yAxis'] = yAxis
	return chart

@app.route('/')
def home():
	chart = createChart()
	return render_template('index.html', image_name='static/img/header.jpg', chart=chart)
 
if __name__ == '__main__':
	app.run(host=cfg['webserver']['host'], port=cfg['webserver']['port'], debug = True)
