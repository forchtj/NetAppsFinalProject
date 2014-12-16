#above this value defines a spike
maxVal = 10

#below this value defines a dip
minVal = 3

#max budget
monthlyBudget = .95

#cost per kilowatt hour
pricePerKilowatt = .12

#Email to send alerts to
to = 'dkrulick@vt.edu'


#########################################################
# DO NOT EDIT BELOW THIS LINE
#########################################################

#for managing timings
import time

#for email sending
import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
import datetime

#for influxdb
from influxdb import InfluxDBClient
from random import randint

#definitions
SPIKE = "spike"
DIP = "dip"
OVERBUDGET = "overbudget"

#toggle to prevent message spam for budget
toggleOverBudget = 0

maxVal = 0
minVal = 0

runningAverage = 0;

#boolean to enable functionality
boolMax = 1;
boolMin = 1;
boolBudget = 1;

#main method - loops to call other methods
def main():
		

	setupEmailInformation(targetEmail)
	
	#start time
	global previousTime
	previousTime = getCurrentDateTime()

	#main control loop
	while (1):
		time.sleep(1)
		evaluate(getValuesSinceLastPull())

#to set up e-mailing information and opening communication with gmail
def setupEmailInformation():
	global gmail_user
	global gmail_password
	global smtpserver
	gmail_user = 'vtteamtemplar@gmail.com'
	gmail_password = 'VirginiaTech'
	smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(gmail_user, gmail_password)

#returns date and time in form for the database requests
def getCurrentDateTime():
	time = datetime.datetime.now()
	return str(time)[:str(time).find('.')]
	
#receives values and determines if thresholds are met
def evaluate(values):
	if(values != []):
		#check for spikes and dips
		if(boolMax and max(values) > maxVal):
			alarm(SPIKE, max(values))
		if(boolMin and min(values) < minVal):
			alarm(DIP, min(values))
		
		
		updateRunningAverage(values)
		#check for budgeting 
		if(boolBudget):
			if(runningAverage*pricePerKilowatt > monthlyBudget*3.6):
				if(toggleOverBudget == 0):
					alarm(OVERBUDGET, runningAverage*pricePerKilowatt*3.6)
					toggleOverBudget = 1
			elif(runningAverage*pricePerKilowatt*3.6 <= .9*monthlyBudget):
				toggleOverBudget = 0
	
#called when an alarm is tripped and sends e-mail
def alarm(alarmtype, numberAlarm):
	#provided from google regarding interfacing with gmail
	today = datetime.date.today()
	arg='ip route list'
	p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
	data = p.communicate()
	split_data = data[0].split()
	ipaddr = split_data[split_data.index('src')+1]
	my_ip = 'Alarm tripped: %s \n Registered value of %s' %  (alarmtype, numberAlarm)
	msg = MIMEText(my_ip)
	msg['Subject'] = 'An alarm was tripped'
	msg['From'] = gmail_user
	msg['To'] = to
	smtpserver.sendmail(gmail_user, [to], msg.as_string())

	#used to keep track of the running average for budget concerns
def updateRunningAverage(values):
	global runningAverage
	newAverage = getAverage(values)
	if(runningAverage == 0):
		runningAverage = newAverage
	else:
		runningAverage = runningAverage*179/180 + newAverage/180
	return runningAverage

	#returns the average of values in a list
def getAverage(values):
	valSum = 0
	for value in values:
		valSum = valSum + value
	return(valSum*1.0/len(values))


#returns values for the next iteration
def getValuesSinceLastPull():
	global previousTime
	currentTime = getCurrentDateTime()
	
	valueslist = []

	#same time, no data will be pulled
	if (currentTime == previousTime):
		valueslist = []
	else:
		values = getIntervalPoints(previousTime, currentTime)
		if values != []:
			for point in values[0]["points"]:
				valueslist.append(point[2]) #extracts data from dict
	
	
	previousTime = currentTime
		

	return valueslist

#formats for time points are YYYY-MM-DD HH:MM:SS
#returns dict with values
def getIntervalPoints(string1, string2):
	db = InfluxDBClient('localhost', '8086', 'root', 'root', 'power')
	dataquery = 'select instant_power from sensor where time > ' + '\''+string1+'\'' + ' and time < ' + '\''+string2 +'\''
	result = db.query(dataquery)
	return result

#maxVal, minVal, monthlyBudget, pricePerKilowatt, targetEmail
if __name__ == "__main__": main()
