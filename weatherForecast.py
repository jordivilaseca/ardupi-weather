#!/usr/bin/python

import urllib.request as UR
import math
import xml.etree.ElementTree as ET
import unicodedata

class weather:
	# ponderacions de vic, manresa, berga respectivament
	tempPond = [0.46, 0.231, 0.309]

	def __init__(self):
		sock = UR.urlopen("http://static-m.meteo.cat/content/opendata/ctermini_comarcal.xml")
		weatherSource = sock.read()                  
		sock.close()
		self.weatherRoot = ET.fromstring(weatherSource)

		self.setDays()
		self.setWeatherForecast(24)
		self.setTemp()

	def id2forecast(self, id):
		symbols = self.weatherRoot.findall("simbol")
		return symbols[int(id)-1].attrib["nomsimbol"]

	def setWeatherForecast(self, id):
		all = self.weatherRoot.findall("prediccio")
		day1 = all[id-1][0].attrib
		day2 = all[id-1][1].attrib
		self.forecast = []
		self.forecast.append (self.id2forecast(day1["simbolmati"].split(".")[0]))
		self.forecast.append (self.id2forecast(day1["simboltarda"].split(".")[0]))
		self.forecast.append (self.id2forecast(day2["simbolmati"].split(".")[0]))
		self.forecast.append (self.id2forecast(day2["simboltarda"].split(".")[0]))

	def getTemps(self, id):
		temps = []
		forecast = self.weatherRoot.findall("prediccio")[id-1]
		temps.append(forecast[0].attrib["tempmax"])
		temps.append(forecast[0].attrib["tempmin"])
		temps.append(forecast[1].attrib["tempmax"])
		temps.append(forecast[1].attrib["tempmin"])
		return temps
		

	def calcTemp(self, Tvic, Tmanresa, Tberga):
		return int(Tvic)*self.tempPond[0]+int(Tmanresa)*self.tempPond[1]+int(Tberga)*self.tempPond[2]

	def setTemp(self):
		all = self.weatherRoot.findall("prediccio")
		vic = self.getTemps(24)
		manresa = self.getTemps(7)
		berga = self.getTemps(14)
		self.forecastTemp = []
		self.forecastTemp.append(self.calcTemp(vic[0],manresa[0], berga[0]))
		self.forecastTemp.append(self.calcTemp(vic[1],manresa[1], berga[1]))
		self.forecastTemp.append(self.calcTemp(vic[2],manresa[2], berga[2]))
		self.forecastTemp.append(self.calcTemp(vic[3],manresa[3], berga[3]))


	def setDays(self):
		first = self.weatherRoot.find("prediccio")
		self.day1 = first[0].attrib["data"]
		self.day2 = first[1].attrib["data"]

prova = weather()
print (prova.day1, prova.day2, prova.forecast[0], prova.forecast[1], prova.forecast[2], prova.forecast[3])
print (prova.forecastTemp[0], prova.forecastTemp[1], prova.forecastTemp[2], prova.forecastTemp[3])