import os
import glob
import sys
import re
import time
import subprocess
import MySQLdb as mdb 
import datetime
 
databaseUsername="root" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="admin" #YOUR MYSQL PASSWORD 
databaseName="DB" 

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def saveToDatabase(temperature):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()
        now=datetime.datetime.now()
        ti=datetime.datetime.now().time()


        with con:
                cur=con.cursor()
                cur.execute("INSERT INTO ds18b20 (temperature,dateMeasured, hourMeasured) VALUES (%s,%s,%s)",(temperature,currentDate,ti))
                print 'temperature ds18b20 : %.1f C'%temperature
		print "Saved temperature"
		return "true"




def read_temp_raw():
	catdata = subprocess.Popen(['cat',device_file], 
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catdata.communicate()
	out_decode = out.decode('utf-8')
	lines = out_decode.split('\n')
	return lines

 
def read_temp():
    lines = read_temp_raw()
  
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return saveToDatabase(temp_c)
	


#check if table is created or if we need to create one
try:
	queryFile=file("createTable.sql","r")

	con=mdb.connect("localhost", databaseUsername,databasePassword,databaseName)
        currentDate=datetime.datetime.now().date()

        with con:
		line=queryFile.readline()
		query=""
		while(line!=""):
			query+=line
			line=queryFile.readline()

		cur=con.cursor()
		cur.execute(query)	
        	#now rename the file, because we do not need to recreate the table everytime this script is run
		queryFile.close()
        	os.rename("createTable.sql","createTable.sql.bkp")
       

except IOError:

        saveToDatabase(read_temp())



