from config import cfg, dataPath
import json

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def getHistoryChart(chartCFG):
	colors = cfg['webserver']['charts']['colors']
	rawData = readJsonData(dataPath + 'history.json')
	chart = {}
	series = []
	yAxis = []
	top = 0
	axisNum = 0
	i = 0
	for panel in chartCFG['panels']:
		for value in panel['values']:
			tooltip = {'valueSuffix' : panel['units'].encode('utf-8')}
			data = [[d[0],d[1][i]] for d in rawData['data']]
			series.append({'type':panel['type'],'name':value,'data': data, 'yAxis': axisNum, 'tooltip' : tooltip ,'connectNulls': 'true', 'color':colors[i]})
			i += 1
		currYAxis = {}
		currYAxis['title'] = {'text': panel['name']}
		currYAxis['height'] = str(panel['height']) + '%'
		currYAxis['top'] = str(top)+'%'
		currYAxis['offset'] = 0
		currYAxis['labels'] = {'align': 'right', 'x': -3}
		if 'min' in panel:
			currYAxis['min'] = panel['min']
		if 'max' in panel:
			currYAxis['max'] = panel['max']
		yAxis.append(currYAxis)
		top += panel['height'] + panel['offset']
		axisNum += 1

	chart['height'] = cfg['webserver']['charts']['history']['height']
	chart['chartID'] = 'history_chart'
	chart['series'] = series
	chart['chartName'] = chartCFG['name']
	chart['yAxis'] = yAxis
	return chart

def getDailyHistoryChart(chartCFG):
	colors = cfg['webserver']['charts']['colors']
	rawData = readJsonData(dataPath + 'dailyHistory.json')
	chart = {}
	series = []
	yAxis = []
	top = 0
	axisNum = 0
	i = 0
	for panel in chartCFG['panels']:
		tooltip = {'valueSuffix' : panel['units'].encode('utf-8')}
		for value in panel['values']:
			if chartCFG['showAVG']:
				AVGdata = [[d[0],d[1][i*3+2]] for d in rawData['data']]
				series.append({'type': 'spline', 'name':value + ' AVG', 'yAxis': axisNum, 'tooltip': tooltip,'connectNulls': 'true', 'data': AVGdata, 'zIndex': 1, 'color': colors[i], 'minTickInterval': 24 * 3600 * 1000})

			if chartCFG['showMINMAX']:
				MINMAXdata = [[d[0],d[1][i*3],d[1][i*3+1]] for d in rawData['data']]
				series.append({'type' : 'areasplinerange', 'name' : value + ' range', 'yAxis': axisNum, 'tooltip' : tooltip, 'connectNulls' : 'true', 'data' : MINMAXdata, 'zIndex': 0, 'lineWidth': 0, 'linkedTo': ':previous', 'fillOpacity': 0.3, 'color': colors[i], 'minTickInterval': 24 * 3600 * 1000})
			i += 1
		currYAxis = {}
		currYAxis['title'] = {'text': panel['name']}
		currYAxis['height'] = str(panel['height']) + '%'
		currYAxis['top'] = str(top)+'%'
		currYAxis['offset'] = 0
		currYAxis['labels'] = {'align': 'right', 'x': -3}
		if 'min' in panel:
			currYAxis['min'] = panel['min']
		if 'max' in panel:
			currYAxis['max'] = panel['max']
		yAxis.append(currYAxis)
		top += panel['height'] + panel['offset']
		axisNum += 1

	chart['height'] = cfg['webserver']['charts']['history']['height']
	chart['chartID'] = 'daily_history_chart'
	chart['series'] = series
	chart['chartName'] = chartCFG['name']
	chart['yAxis'] = yAxis
	return chart

def getChart(key,chartCFG):
	if not chartCFG['enable']:
		return None

	if key == 'history':
		return getHistoryChart(chartCFG);
	else:
		return getDailyHistoryChart(chartCFG);
	

class chartManager:

	def __init__(self):
		pass

	def getChart(self, id):
		return getChart(id, cfg['webserver']['charts'][id])
