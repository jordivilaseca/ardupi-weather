from config import cfg, DATA_PATH
import json

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def createHistoryChart():
	chartCFG = cfg['webserver']['charts']['history']
	colors = cfg['webserver']['charts']['colors']
	names = cfg['webserver']['names']['sensors']
	rawData = readJsonData(DATA_PATH + 'history.json')
	chart = {}
	series = []
	yAxis = []
	top = 0
	axisNum = 0
	i = 0

	for panel in chartCFG['panels']:
		for value in panel['values']:
			tooltip = {'valueSuffix' : panel['units']}
			series.append({'type':panel['type'],'name':names[value],'data': [], 'yAxis': axisNum, 'tooltip' : tooltip ,'connectNulls': 'true', 'color':colors[i]})
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
	chart['name'] = chartCFG['name']
	chart['yAxis'] = yAxis
	return chart

def createDailyHistoryChart():
	chartCFG = cfg['webserver']['charts']['dailyHistory']
	colors = cfg['webserver']['charts']['colors']
	names = cfg['webserver']['names']['sensors']
	avgName = cfg['webserver']['names']['average']
	rangeName = cfg['webserver']['names']['range']
	rawData = readJsonData(DATA_PATH + 'dailyHistory.json')
	chart = {}
	series = []
	yAxis = []
	top = 0
	axisNum = 0
	i = 0
	for panel in chartCFG['panels']:
		tooltip = {'valueSuffix' : panel['units']}
		for value in panel['values']:
			if chartCFG['showAVG']:
				series.append({'type': 'spline', 'name':names[value] + ' ' + avgName, 'yAxis': axisNum, 'tooltip': tooltip,'connectNulls': 'true', 'data': [], 'zIndex': 1, 'color': colors[i], 'minTickInterval': 24 * 3600 * 1000})

			if chartCFG['showMINMAX']:
				series.append({'type' : 'areasplinerange', 'name' : names[value] + ' ' + rangeName, 'yAxis': axisNum, 'tooltip' : tooltip, 'connectNulls' : 'true', 'data' : [], 'zIndex': 0, 'lineWidth': 0, 'linkedTo': ':previous', 'fillOpacity': 0.3, 'color': colors[i], 'minTickInterval': 24 * 3600 * 1000})
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
	chart['name'] = chartCFG['name']
	chart['yAxis'] = yAxis
	return chart	

class chartManager:

	def __init__(self):
		self.charts = {}
		if cfg['webserver']['charts']['history']['enable']:
			self.charts['history'] = createHistoryChart()
		if cfg['webserver']['charts']['dailyHistory']['enable']:
			self.charts['dailyHistory'] = createDailyHistoryChart()

	def getChart(self, id):
		return self.charts[id]