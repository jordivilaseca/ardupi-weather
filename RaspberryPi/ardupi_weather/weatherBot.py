import telebot
import commands
from config import LOG_PATH

from os import listdir
from os.path import isfile, join

API_TOKEN = "api_key"
bot = telebot.TeleBot(API_TOKEN)

print (bot.get_me())

def help():
	return ''' Available commands:\n \
	- \help -> General information about the bot.\n \
	- \status -> Status of the station.\n \
	- \logs -> Show all log files available with format <index>.<name>\n \
	- \log_<index> -> Show log information of the file <index>'''

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	bot.reply_to(message, "Welcome to the Weather Station telegram bot!!\n\n" + help())

@bot.message_handler(commands=['status'])
def send_station_status(message):
	keys = ['station.py']

	output = commands.getoutput('ps -A')

	m = ""
	for key in keys:
		m = m + '-' + key + ': '
		if key in output:
			m += 'OK\n'
		else:
			m += 'NOT WORKING!\n'

	bot.reply_to(message, m)

@bot.message_handler(commands=['logs'])
def send_logs_names(message):
	files = ""
	i = 0
	for f in listdir(LOG_PATH):
		if isfile(join(LOG_PATH,f)):
			files += str(i)  + "." + f + "\n"
			i += 1
	bot.reply_to(message, files)

def log_usage(m):
	return 'ERROR: ' + m + '. Usage: log <index>'

@bot.message_handler(func=lambda message: message.text.startswith('/log '))
def send_logs_names(message):
	listfiles = [f for f in listdir(LOG_PATH) if isfile(join(LOG_PATH,f))]

	command = message.text.split(' ')
	index = -1;
	if len(command) == 2:
		try:
			index = long(command[1])
		except:
			bot.reply_to(message,log_usage('Not number'))
		else:
			if index >= 0 and index < len(listfiles):
				data = ""
				with open(join(LOG_PATH,listfiles[index]), 'r') as f:
					data = f.read()
				bot.reply_to(message, data)
			else:
				bot.reply_to(message,log_usage('Index out of range'))
	else:
		bot.reply_to(message,log_usage('Too many parameters'))

@bot.message_handler(commands=['prova'])
def prova(message):
	bot.reply_to(message, str(message))

bot.polling()
