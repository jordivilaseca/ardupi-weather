#!/usr/bin/env python3

import os

# Application path
APP_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

# Flask files path
FLASK_PATH = APP_PATH + 'flaskfiles/'
STATIC_FLASK_PATH = FLASK_PATH + 'static'
IMAGES_FLASK_RELATIVE_PATH = '/static/img/'
TEMPLATES_FLASK_PATH = FLASK_PATH + 'templates'

# Configuration and temporal files
TEMP_PATH = os.path.expanduser('~/.config/ardupi_weather/')
CONFIG_FILE = 'config.yml'
CONFIG_PATH = TEMP_PATH + CONFIG_FILE
DATA_PATH = TEMP_PATH + 'data/'
LOG_PATH = TEMP_PATH + 'log/'
