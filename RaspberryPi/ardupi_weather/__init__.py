#!/usr/bin/env python3

import shutil
import os
from ardupi_weather.consts import *
import argparse

def copyConfigurationFile():
	shutil.copy(APP_PATH + CONFIG_FILE, CONFIG_PATH)

def createFolder(path):
	os.mkdir(path)

def existsFolder(path):
	return os.path.exists(path) and os.path.isdir(path)

def existsFile(path):
	return os.path.exists(path) and os.path.isfile(path)

def checkTempDirectory():
	if(os.path.exists(TEMP_PATH)):
		if not os.path.isdir(TEMP_PATH):
			print("ERROR: Configuration path '%s' exists but is not a directory" % TEMP_PATH)

		# Check if exists logging path
		if not existsFolder(LOG_PATH):
			createFolder(LOG_PATH)

		# Check if exits data path
		if not existsFolder(DATA_PATH):
			createFolder(DATA_PATH)

		# Check if exists configuration file
		if not existsFile(CONFIG_PATH):
			copyConfigurationFile()

	else:
		# Create configuration folder and import configuration.
		createFolder(TEMP_PATH)
		copyConfigurationFile()

		# Create logging folder.
		createFolder(LOG_PATH)

		# Create data folder
		createFolder(DATA_PATH)

parser = argparse.ArgumentParser()
parser.add_argument('--init', help='Initialize weather station configuration files and directories', action='store_true')
parser.add_argument('--restore-config', help='Restores the default configuration file', action='store_true')
args = parser.parse_args()

# Deal with flags.
if args.init:
	checkTempDirectory()
	exit()
if args.restore_config:
	copyConfigurationFile()
	exit()

# Start no flags execution.
checkTempDirectory()


