#!/usr/bin/python
import sys

import subprocess 
import re 
import os 
import time 
import MySQLdb as mdb 
import datetime
import bmp180 as bmp180

databaseUsername="root"
databasePassword="admin" 
databaseName="WordpressDB" #do not change unless you named the Wordpress database with some other name

bmp180.main()


def saveToDatabase(temperature,pressure):

	con=mdb.connect("localhost", databaseUsername, databasePassword, databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        ti=datetime.datetime.now().time()
	
        with con:
                cur=con.cursor()
		
                cur.execute("INSERT INTO bmp180 (Temperatura,Cisnienie, dateMeasured, hourMeasured) VALUES (%s,%s,%s,%s)",(temperature,pressure,currentDate, ti))

		print "Saved bmp180 mesures"
		return "true"


def readInfo():


        (temperature,pressure) = bmp180.readBmp180()

      
        print "Temperatura : {0} C".format(temperature)
        print "Cisnienie    : {0} HPa".format(pressure)

	if temperature is not None and pressure is not None:
		return saveToDatabase(temperature,pressure) #success, save the readings
	else:
		print 'Failed to get reading. Try again!'
		sys.exit(1)


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
	pass #table has already been created
	

status=readInfo() #get the readings
