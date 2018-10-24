import yaml
import codecs
import os
from ardupi_weather.consts import *

def getPath(path):

	"""
	It returns the path, or the default path (the default data path) if the variable path is equal to "default".

	Args:
		path: The path to a directory.

	Returns:
		A string containing the correct path.
	"""

	return DATA_PATH if path == 'default' else path

def setPath(cfg):

	"""
	It will compute the correct path for each path equals to "default" in a configuration file.

	Args:
		cfg: The configuration file.

	Returns:
		The rectified configuration file.
	"""

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

# Code to execute each time the file is imported.
with codecs.open(CONFIG_PATH, 'r', encoding='utf-8') as ymlfile:
	cfg = yaml.load(ymlfile)

cfg = setPath(cfg)
