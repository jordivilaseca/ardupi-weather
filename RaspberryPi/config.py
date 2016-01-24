import yaml
import codecs
import os

APP_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'
FLASK_PATH = APP_PATH + 'flaskfiles/'
STATIC_FLASK_PATH = FLASK_PATH + 'static'
IMAGES_FLASK_RELATIVE_PATH = '/static/img/'
TEMPLATES_FLASK_PATH = FLASK_PATH + 'templates'
DATA_PATH = APP_PATH + 'data/'
LOG_PATH = APP_PATH + 'log/'

def getPath(path):
	return DATA_PATH if path == 'default' else path

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

with codecs.open("config.yml", 'r', encoding='utf-8') as ymlfile:
	cfg = yaml.load(ymlfile)

cfg = setPath(cfg)