from config import cfg, dataPath
import json

def readJsonData(filePath):
	with open(filePath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def createChart(key,chartCFG):
	keyFile = dataPath + key + '.json'
	rawData = readJsonData(keyFile)
	chart = {}
	series = []
	yAxis = []
	top = 0
	axisNum = 0
	i = 0
	for panel in chartCFG['panels']:
		for value in panel['values']:
			tooltip = {'valueSuffix' : str(panel['units'])}
			data = [[d[0],d[1][i]] for d in rawData]
			series.append({'type':panel['type'],'name':value,'data': data, 'yAxis': axisNum, 'tooltip' : tooltip})
			i += 1
		yAxis.append({'title': {'text': panel['name']}, 'height': str(panel['height'])+'%', 'top': str(top)+'%', 'offset': 0, 'labels': {'align': 'right', 'x': -3}})
		top += panel['height'] + panel['offset']
		axisNum += 1

	chart['height'] = cfg['webserver']['charts']['history']['height']
	chart['chartID'] = key + '_chart'
	chart['series'] = series
	chart['chartName'] = chartCFG['name']
	chart['yAxis'] = yAxis
	return chart

class chartManager:

	def __init__(self):
		pass

	def getChart(self, id):
		return createChart(id, cfg['webserver']['charts'][id])
