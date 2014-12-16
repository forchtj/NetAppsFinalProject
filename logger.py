from influxdb import InfluxDBClient
from random import randint
import smbus
import time
from datetime import datetime
from datetime import timedelta
from bashplotlib.scatterplot import plot_scatter
import json

def init():
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	count = 0
	while True:
		new = getWatts()

		json_body = [{
		    "points": [
		        [new],
		    ],
		    "name": "sensor",
		    "columns": ["instant_power"]
		}]
		db.write_points(json_body)

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

def getWatts():
	#start_time = datetime.now()
	#times = []
	vals = []
	bus = smbus.SMBus(1)
	address = 0x48

	for x in range(0, 200):
		config = 0x00

		# set pga
		config |= 0x0000

		# set sample rate
		config |= 0x0070
	
		# disable comparator
		config |= 0x0003
	
		# set mode 
		config |= 0x0000
	
		# set ports 
		config |= 0x3000
	
		# start conversion
		config |= 0x8000
	
		#print "config:", hex(config)
		config_vals = [(config >> 8) & 0xFF, config & 0xFF]
		# write config bytes 0x01 = config cmd
		bus.write_i2c_block_data(address, 0x01, config_vals)
	
		# write pointer register 0x00 = convert cmd
		bus.write_byte(address, 0x00)
	
		# wait for a bit to let it finish
		delay = 2.0/860
		time.sleep(delay)
		result= bus.read_i2c_block_data(address, 0x0)
		#times.append(millis() )
		#print result[0], result[1] 
	
		val = (result[0] << 8) | (result[1])
		if val > 0x7FFF:
			volt = (val - 0xFFFF)*6144/32768.0
			vals.append(volt)
			#vals.append(val)
		else:
			volt = (val)*6144/32768.0	
			#vals.append(val)
			vals.append(volt)
			
		#print volt
	#f = open("test.txt", 'w')
	#for x in range(0, len(vals) -1):
	#	writestr = str(times[x]) + ' , ' + str(vals[x]) + '\n'
	#	f.write(writestr)
	#f.close()
	#plot_scatter("test.txt", "", "", 30, '.', "white", "Voltage")
	maxval = max(vals)
	avgval = (sum(vals) / len(vals))
	minval = min(vals)
	#print maxval
	#print avgval
	#print minval
	watts =  ((max(vals)- (avgval))/14) * 60
	#print "power =", watts 
	#print "time elapsed (ms)", millis()
	return watts

	
init()