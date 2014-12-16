from influxdb import InfluxDBClient
from random import randint
import json


def init():
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	count = 0
	while count < 100:
		new = randint(0,100)

		json_body = [{
		    "points": [
		        [new],
		    ],
		    "name": "sensor",
		    "columns": ["instant_power"]
		}]
		db.write_points(json_body)
		count = count + 1

#formats for time points are YYYY-MM-DD HH:MM:SS
def getIntervalPoints(string1, string2):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select instant_power from sensor where time > ' + '\''+string1+'\'' + ' and time < ' + '\''+string2 +'\''
	result = db.query(dataquery)
	return result

#returns the average value between the given two time points
def getIntervalAverage(string1, string2):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select mean(instant_power) from sensor where time > ' + '\''+string1+'\'' + ' and time < ' + '\''+string2 +'\''
	result = db.query(dataquery)
	return result

#returns the last x entries with timestamps within the previous 'hours' within a maximum x data points
def getLastXPoints(hours, x):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select instant_power from sensor where time > now() - ' + str(hours) + 'h limit ' + str(x)
	result = db.query(dataquery)
	return result

#returns the average power in the last 'hours' hours within a maximum x data points
def getLastXAverage(hours, x):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select mean(instant_power) from sensor where time > now() - ' + str(hours) + 'h limit ' + str(x)
	result = db.query(dataquery)
	return result
	
#returns the minimum power in last x data points within last 'hours' hours
def getlastXMin(hours, x):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select min(instant_power) from sensor where time > now() - ' + str(hours) + 'h limit ' + str(x)
	result = db.query(dataquery)
	return result