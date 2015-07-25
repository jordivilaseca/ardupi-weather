import yaml
import os

appPath = os.path.dirname(os.path.realpath(__file__))
flaskPath = appPath + '/flaskfiles/'
staticFlaskPath = flaskPath + 'static'
templatesFlaskPath = flaskPath + 'templates'
dataPath = appPath + '/data/'

def getPath(path):
	return dataPath if path == 'default' else path

def setPath(cfg):
	nCfg = None
	if isinstance(cfg, dict):
		nCfg = {}
		for key,value in cfg.items():
			if key == 'path':
				nCfg[key] = getPath(value)
			else:
				nCfg[key] = setPath(value)
	elif isinstance(cfg, list):
		nCfg = []
		for elem in cfg:
			nCfg.append(setPath(elem))
	else:
		nCfg = cfg
	return nCfg

with open("config.yml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile)

cfg = setPath(cfg)