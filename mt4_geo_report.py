#! /usr/bin/env python3
# The script will read the MT4 server logs and generate the reports for higest client latency and geo distribution report in daily or monthly basis.



import collections
import sys
import os
import re
import requests
import csv
import datetime
import glob
from pathlib import Path, PureWindowsPath
from time import sleep


##### default variable #####
tempDir=".\\temp"
dataDir=".\\MT4_Server_Log\\47.88.153.124"
rptDir=".\\report"
raw_data=[]
waitSec = 60
waitRow = 145
autoBool = 0
inputStr = ""





# take a int in minutes & formant and print the waiting message
def printWaitingMsg(minutesCount):
    if ( minutesCount == 0 ):
        print ('[INFO] Will start the reports generation in 1 minutes ...')
    elif ( minutesCount > 0 and minutesCount < 60 ):
        print ('[INFO] Collection of data will be finished in about '+str(minutesCount)+' minutes ...')
    else:
        print ('[INFO] Collection of data will be finished in about '+str((minutesCount / 60.0))+' hours ...')

# take 2 int as intput, formant and print the progress status in %
def printWaitingMsgRate(progCount, finCount):
    
    cRate = round((progCount / finCount * 100.0),1)
    #print ("[INFO] Porgress of the data processing rate is about %s%% ..." % (cRate))
    print ("[INFO] Porgress of the data processing rate is about %s%%  (%s/%s)..." % (cRate, progCount, finCount))
    


# Digest the MT4 app log, then return / append an array of the data for the reports
# Accepting below variables : logPath,
def generateRawList(logPath):

    # validate the target data exists in the data dir 
    if len(glob.glob(logPath)) == 0: 
        print ("[ERROR] *****The data in "+logPath+" is not available, the script exits... !!!!!*****")
        sys.exit( )
        

    #Get the line count for progress estaimation
    num_lines = 0
    tempArray = []
    for fileName in glob.glob(logPath):
        for line in open(fileName, encoding='latin-1'):
            if re.search(r'\'88[0-9]+\'.*login',line):
                line = line.replace('\'','').replace('dc: ','dc:').replace(',',' ').replace('	',' ')
                tempArray.append(list(line.split(" "))[2])


    expectedCount = (int(len(tempArray)))
    print ("[INFO] Starting to collect the location data from the 3rd party API ...")
    printWaitingMsgRate(0, expectedCount)
    sleep(waitSec)

    countRow = 0
    skipHttp_bool = 0
    for fileName in glob.glob(logPath):
        with open(fileName, 'r', encoding='latin-1') as f:
            for x in f:

              if re.search(r'\'88[0-9]+\'.*login',x):
                x = x.replace('\'','').replace('dc: ','dc:').replace(',',' ').replace('	',' ')
                l = list(x.split(" "))

                if len(l) > 14:


                    # Do not call the http request if the record has been stored
                    for index in range (0,len(raw_data)):
                        if str(l[2]) == str((raw_data[index][0])):
                            # Item : IP, Region, Data_Center, latency(ms)
                            raw_data.append([l[2],raw_data[index][1], l[9], l[15]])
                            skipHttp_bool = 1
                            break

                    if skipHttp_bool is 0:
                        httpLink='http://ip-api.com/csv/'+l[2]+'?lang=zh-CN'
                        response = requests.get(httpLink)
                        buffList = list(response.text.split(","))
                        # Item : IP, Region, Data_Center, latency(ms)
                        raw_data.append([l[2],buffList[4], l[9], int(l[15])])
                        countRow+=1
                    else:
                        skipHttp_bool = 0
                        continue

                    # For Debug only
                    #raw_data.append([l[2], l[9], l[15]])
                    #print (raw_data[-1])
                    #printWaitingMsgRate(len(raw_data), expectedCount)                    

                if (countRow % waitRow) == 0:
                    countRow = 0
                    printWaitingMsgRate(len(raw_data), expectedCount)                    
                    sleep(waitSec)
    
    printWaitingMsgRate(len(raw_data), expectedCount)                    





#Generate the given highest latency report by the raw_data
def genHighestLatencyRpt(num):

    #remove duplicated record
    myList = []
    tempList = sorted(raw_data,key=lambda l:int(l[3]), reverse=True)
    
    expCount = len(tempList)
    for i in range(0,expCount):
        if i is 0: myList.append(tempList[i])
        if myList[-1] != tempList[i]:  myList.append(tempList[i])
        if (i / expCount) * 100 % 10 == 0: printWaitingMsgRate(i, expCount)

    if num == 0 or num > len(myList):
        #print ("[INFO] The total number of the extracted data %d is less than the required %d records..." % (len(myList), num))
        num = len(myList)

    print ("[INFO] Starting to generate the hlRptPath ...")
    
    tString = "IP, Region, Data Center, Ping Latency(ms)\n"
    f= open(hlRptPath,"wb")
    f.write(tString.encode('utf-8-sig'))

    lineCount = 0
    for index in range(0,len(myList)):
        
        tString = (','.join(str(item) for item in myList[index]))+"\n"
        f.write(tString.encode('utf-8-sig'))

        if lineCount >= num: break
        lineCount+=1

    f.close()

    if (os.path.isfile(hlRptPath)):
        print ("[INFO] The "+hlRptPath+" has been generated ... !")
    else:
        print ("[ERROR] The "+hlRptPath+" cannot be generated ... !")

    return (myList)



#3. Generate the Geo location report
def genGeoLocationRpt():

    myList = sorted(raw_data,key=lambda l:l[0], reverse=True)
    buffList = []
    regionList = []

    # retrive the IP & location data & sort the array
    expCount = len(myList)
    for i in range(0, expCount):
       
        if (i / expCount) * 100 % 10 == 0: printWaitingMsgRate(i, expCount)
        
        if len(buffList) != 0:
            if buffList[-1] != [myList[i][0], myList[i][1]]:
                buffList.append([myList[i][0], myList[i][1]])
        else:
            buffList.append([myList[i][0], myList[i][1]])


    print ("[INFO] The raw data arrway has been stroed ...")

    #Generate the Geo distribution report
    print ("[INFO] Starting to generate the "+geoRpPath+" ...")
    
    tString = "Region, Hit Count\n"
    f= open(geoRpPath,"wb")
    f.write(tString.encode('utf-8-sig'))

    # Count the region in the unique IP list
    for i in range(0,len(buffList)):
        regionList.append(buffList[i][1])

    for i in (collections.Counter(regionList).most_common()):
        #print (tString)
        tString = (str(i[0])+","+str(i[1])+"\n")
        f.write(tString.encode('utf-8-sig'))

    f.close()

    if (os.path.isfile(geoRpPath)):
        print ("[INFO] The "+geoRpPath+" has been generated ... !")
    else:
        print ("[ERROR] The "+geoRpPath+" cannot be generated ... !")




##### main #####

#0. Define the report date & path

# For debug only
# print ("[INFO] The programe has been started at "+str(datetime.datetime.now())+"...")

if len(sys.argv) > 1:
    if str(sys.argv[1]) == "auto":
        autoBool = 1
    elif re.search(r'[0-9][0-9][0-9][0-9]+',str(sys.argv[1])):
       inputStr = (sys.argv[1])
       autoBool = 1

if autoBool == 1 and inputStr == "":
    buffDate = datetime.date.today()
    inputStr = (buffDate.strftime("%Y%m%d"))
    print ("[INFO] Auto mode is On - "+inputStr+" data will be useded...")
elif inputStr == "":
    inputStr = input('Please Input the date string (YYYYMMDD / YYYYMM):')

dataPath = dataDir+"\\"+inputStr+"*.log"
hlRptPath=rptDir+"\\highest_latency_rpt_"+inputStr+".csv"
geoRpPath=rptDir+"\\geo_distribution_rpt_"+inputStr+".csv"



#1. Digest the MT4 app log, then return / append an array of the data for the reports
generateRawList(dataPath)

#2. Generate the highest latency report by the given no# (default 0 to print all)
genHighestLatencyRpt(50)

#3. Generate the Geo location report
genGeoLocationRpt()

# For debug only
# print ("[INFO] The programe has been ended at "+str(datetime.datetime.now())+"...!")
