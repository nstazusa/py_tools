#! /usr/bin/env python3
#
#   This application is to input the target parameters and scan for any message gap in the specificed log.
#
#

from tkinter import *
from tkinter import scrolledtext
import os
import re
import glob
import threading
from time import gmtime, strftime
import datetime
from datetime import datetime, timedelta

# Local variable & initial
tDate="TODAY"
tempDir=".\\temp"
dataDir=".\\data\\CheetahSfc(172.19.43.15)\\"
baseDirpath=""
delayThreshold=60
tSymbol="ALL"
feedName=""
resourceLock=0



# Create a lable in the app
class LableObj:
    def __init__(self, winApp, displayText, colNum, rowNum):
        self.winApp = winApp
        self.displayText = displayText
        self.colNum = colNum
        self.rowNum = rowNum
        self.columnspan = 1

        self.lableName = Label(self.winApp, text=self.displayText)
        self.lableName.grid(column=self.colNum, row=self.rowNum, columnspan=self.columnspan)

    def updateText(self):
        self.lableName.configure(text=self.displayText)

    def updateColSpan(self, columnspan):
        self.lableName.grid(columnspan=columnspan)

# Create a button in the app
class ButtonObj:
    def __init__(self, winApp, displayText, colNum, rowNum, cmdInput):
        self.winApp = winApp
        self.displayText = displayText
        self.colNum = colNum
        self.rowNum = rowNum
        self.cmdInput = cmdInput
        self.columnspan = 1

        btnName = Button(self.winApp, text=self.displayText,command=self.cmdInput)
        btnName.grid(column=self.colNum, row=self.rowNum)

#Create a textbox
class TextBoxObj:
    def __init__(self, winApp, displayText, colNum, rowNum, widthNum, colSpan):
        self.winApp = winApp
        self.displayText = displayText
        self.colNum = colNum
        self.rowNum = rowNum
        self.widthNum = widthNum
        self.columnspan = colSpan

        self.textBox = Entry(self.winApp,width=self.widthNum)
        self.textBox.insert(END, self.displayText)
        self.textBox.grid(column=self.colNum, row=self.rowNum, columnspan=self.columnspan)


    def updateText(self):
        self.textBox.delete(0, END)
        self.textBox.insert(END, self.displayText)

    def getText(self):
        return self.textBox.get()


#Create a scrolledTextBox
class ScTextBoxObj:
    def __init__(self, winApp, colNum, rowNum, widthNum, heightNum, colSpan):
        self.winApp = winApp

        self.colNum = colNum
        self.rowNum = rowNum
        self.widthNum = widthNum
        self.heightNum = heightNum
        self.columnspan = colSpan

        #self.displayText = ""

        self.textGrid = scrolledtext.ScrolledText(self.winApp,width=self.widthNum,height=self.heightNum)
        self.textGrid.grid(column=self.colNum,row=self.rowNum, columnspan=self.columnspan)

    def insertText(self, inputText):
             self.textGrid.insert(INSERT, inputText)
             self.textGrid.yview_pickplace("end")

    def insertTextInRed(self, inputText):
             self.textGrid.insert(INSERT, inputText, 'alert')
             self.textGrid.tag_config('alert', foreground='red')
             self.textGrid.yview_pickplace("end")

    def clearText(self):
             self.textGrid.delete(1.0, END)





# Collection of click functions
def click4ProdBB():
    inputTbox1.displayText = "Emperor CheetahSfc ProdBB"
    inputTbox1.updateText()

def click4ProdMT4BB():
    inputTbox1.displayText = "Emperor CheetahSfc ProdMT4BB"
    inputTbox1.updateText()

def click4ProdMT4BBBGNE():
    inputTbox1.displayText = "Emperor CheetahSfc ProdMT4BBBGNE"
    inputTbox1.updateText()

def click4ProdRingusBB():
    inputTbox1.displayText = "Emperor CheetahSfc ProdRingusBB"
    inputTbox1.updateText()

def click4getConfig():

    feedName = inputTbox1.getText()
    tDate = inputTbox2.getText()
    baseDirpath=dataDir+str(inputTbox1.getText())
    tSymbol = inputTbox3.getText()
    delayThreshold = inputTbox4.getText()

    #valid tDate value
    sysMsg = ""
    if (re.search(r'^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$', tDate)) == None and tDate != "TODAY":
        tDate = "TODAY"
        sysMsg+="Date format is incorrect, TODAY will be used! "

    if feedName == "Input / Select Feed Dir Name":
        sysMsg+="Please select correct feed name! "


    inputTbox5.displayText = tDate
    inputTbox5.updateText()
    inputTbox6.displayText = baseDirpath
    inputTbox6.updateText()
    inputTbox7.displayText = tSymbol
    inputTbox7.updateText()
    inputTbox8.displayText = delayThreshold
    inputTbox8.updateText()

    inputTbox9.displayText = sysMsg
    inputTbox9.updateText()
    #Refreh GUI to display the result
    winsAppBlock.update()

    # For debug only
    #print (feedName, tDate, baseDirpath, tSymbol, delayThreshold)
    #print (PureWindowsPath(baseDirpath))


def clickTodayDate():
    inputTbox2.displayText = tDate
    inputTbox2.updateText()


def clickPreDate():

    bDate = inputTbox2.getText()
    if bDate == "TODAY":
        bDate = datetime.today().strftime('%Y-%m-%d')

    if (datetime.strptime(bDate, "%Y-%m-%d") - timedelta(days=1)).strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d'):
        inputTbox2.displayText = "TODAY"
    else:
        inputTbox2.displayText = (datetime.strptime(bDate, "%Y-%m-%d") - timedelta(days=1)).strftime('%Y-%m-%d')

    inputTbox2.updateText()


def clickNextDate():

    bDate = inputTbox2.getText()
    if bDate == "TODAY":
        bDate = datetime.today().strftime('%Y-%m-%d')

    if (datetime.strptime(bDate, "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d'):
        inputTbox2.displayText = "TODAY"
    else:
        inputTbox2.displayText = (datetime.strptime(bDate, "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%d')

    inputTbox2.updateText()


def clickDefSymbol():
    inputTbox3.displayText = tSymbol
    inputTbox3.updateText()


def click4ScanBBLog():

    #Retrive the config from the object
    sDate=(inputTbox5.getText())
    baseDirpath=(inputTbox6.getText())
    tSymbol = inputTbox7.getText()
    delayThreshold = inputTbox8.getText()



    # Modify the logPath according to the Symbol
    if tSymbol != "ALL":
        baseDirpath+="\\log\\*\\*"+tSymbol+"*"
    else:
        baseDirpath+="\\log\\*\\"

    # Modify the logPath according to the date
    if sDate != "TODAY":
        logPath = baseDirpath+"*"+sDate+"*"
    else:

        logPath = baseDirpath+"*"



    #print (feedName, tDate, baseDirpath, tSymbol, delayThreshold)
    mainTextBox.clearText()
    mainTextBox.insertText("[INFO] ***** Starting to Scan the "+logPath+" log(s) *****\n")

    # Start the threats for the log scan
    threads = [i for i in range(0, len(glob.glob(logPath)))]
    t = 0
    for fileName in glob.glob(logPath):

        if sDate == "TODAY":
            if (re.search(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}', fileName)) == None:
                mainTextBox.insertText("[INFO] Processing "+fileName+" ...\n")
                threads[t] = threading.Thread(target=scanLogForGap, args=(fileName, delayThreshold))
                threads[t].start()
                t+=1
        else:
            mainTextBox.insertText("[INFO] Processing "+fileName+" ...\n")
            threads[t] = threading.Thread(target=scanLogForGap, args=(fileName, delayThreshold))
            threads[t].start()
            t+=1

    #mainTextBox.insertText("[INFO] ***** Scanning has been completed *****\n")



# to scan a log file and find any gat > delySec
def scanLogForGap(tFile, delaySec):

    #cTimeStr = getCurrentTime("%Y-%m-%d %H:%M:%S")
    #mainTextBox.insertText("[INFO]"+cTimeStr+" ***** Scanning of "+tFile+" has been started *****\n")
    pLine = ""
    pTimeInSec = 0

    with open(tFile, 'r') as readLine:
        for l in readLine:
            l = l.replace("\n", "", 1)
            l = l.replace(",", " ", 1)
            l = l.split(' ')


            #retrieve the time string of the line
            try:
                buffString = str(l[1])
            except IndexError:
                print ("[Exception] ****** Below line has been skipped due to unexpected line format ******")
                print ("[Exception] Processing file: "+tFile)
                print (l)
                pass

            hh = buffString[0:2]
            mm = buffString[2:4]
            ss = buffString[4:]

            try:
                cTimeInSec = int(hh) * 3600 + int(mm) * 60 + int(ss)
                if pTimeInSec == 0:
                    pLine = l
                    pTimeInSec = cTimeInSec
                    continue
                else:
                    diffInSec = cTimeInSec - pTimeInSec

                    if int(diffInSec) > int(delaySec):

                        cTimeStr = getCurrentTime("%Y-%m-%d %H:%M:%S")
                        mainTextBox.insertTextInRed("[Alert]"+cTimeStr+"With "+str(diffInSec)+" sec gap detected in "+tFile+" below lines: \n"+str(pLine)+"\n"+str(l)+"\n")
                        #mainTextBox.insertText("[Debug] "+str(cTimeInSec)+"-"+str(pTimeInSec)+"="+delaySec+"\n")
                        #mainTextBox.insertText("[Debug] "+str(hh)+","+str(mm)+","+str(ss)+","+buffString+"\n")

                    # assigs for pervious line record
                    pTimeInSec = cTimeInSec
                    pLine = l

            except ValueError:
                print ("[Exception] ****** Below line has been skipped due to unexpected line value ******")
                print ("[Exception] Processing file: "+tFile)
                print (l)
                pass

                #debug only
                #print ("[Debug] Time diff: "+str(diffInSec)+", Current Time: "+(buffString))

    cTimeStr = getCurrentTime("%Y-%m-%d %H:%M:%S")
    mainTextBox.insertText("[INFO]"+cTimeStr+" "+tFile+" completed *** !\n")



# Privde a time formating string, then return the current time string
def getCurrentTime(timeStr):
    return strftime(timeStr)




##### Main #####
if __name__ == "__main__":

    winsAppBlock = Tk()
    winsAppBlock.title("Bloomberg Feed Log Validator")
    winsAppBlock.geometry('1200x1000')

    titleBar = LableObj(winsAppBlock, "Welcome to Bloomberg Feed Log Validator",0,0)
    titleBar.updateColSpan(2)

    exitButton = ButtonObj(winsAppBlock, "EXIT", 3, 0 ,exit)

    titleTbo1 = LableObj(winsAppBlock, "Target Feed: ", 0, 1)
    inputTbox1 = TextBoxObj(winsAppBlock, "Input / Select Feed Dir Name", 1, 1, 50, 10)
    titleTbo2 = LableObj(winsAppBlock, "Target Date: ", 0, 2)
    inputTbox2 = TextBoxObj(winsAppBlock, tDate, 1, 2, 50, 10)

    pDateBlt = ButtonObj(winsAppBlock, "Previous Day", 10, 2 , clickPreDate)
    cDateBlt = ButtonObj(winsAppBlock, "TODAY", 11, 2 , clickTodayDate)
    nDateBlt = ButtonObj(winsAppBlock, "Next Day", 12, 2 , clickNextDate)

    titleTbo3 = LableObj(winsAppBlock, "Target Symbol: ", 0, 3)
    inputTbox3 = TextBoxObj(winsAppBlock, tSymbol, 1, 3, 50, 10)
    defaultSymbol = ButtonObj(winsAppBlock, "ALL", 10, 3 , clickDefSymbol)

    titleTbo4 = LableObj(winsAppBlock, "Data interval (Seconds): ", 0, 4)
    inputTbox4 = TextBoxObj(winsAppBlock, delayThreshold, 1, 4, 50, 10)

    titleBar1 = LableObj(winsAppBlock, "Choose defined feed: ", 0, 5)
    feed1Button = ButtonObj(winsAppBlock, "ProdBB",          0, 6 , click4ProdBB)
    feed2Button = ButtonObj(winsAppBlock, "ProdMT4BB",       0, 7 , click4ProdMT4BB)
    feed3Button = ButtonObj(winsAppBlock, "ProdMT4BBBGNE",   0, 8 , click4ProdMT4BBBGNE)
    feed4Button = ButtonObj(winsAppBlock, "ProdRingusBB",    0, 9 , click4ProdRingusBB)

    titleBar2 = LableObj(winsAppBlock, "Click to confirm the above setup: ", 0, 10)
    getInfoButton = ButtonObj(winsAppBlock, "Get Config", 1, 10 , click4getConfig)

    titleBar4 = LableObj(winsAppBlock, "Below Setup will be used: ", 0, 12)
    titleBar5 = LableObj(winsAppBlock, "Target Log Date: ", 0, 13)
    titleBar6 = LableObj(winsAppBlock, "Target Log Path: ", 0, 14)
    titleBar7 = LableObj(winsAppBlock, "Target Symbol: ", 0, 15)
    titleBar8 = LableObj(winsAppBlock, "Delay Thershold (seconds): ", 0, 16)
    titleBar9 = LableObj(winsAppBlock, "System Message: ", 0, 17)

    inputTbox5 = TextBoxObj(winsAppBlock, "", 1, 13, 60, 10)
    inputTbox6 = TextBoxObj(winsAppBlock, "", 1, 14, 60, 10)
    inputTbox7 = TextBoxObj(winsAppBlock, "", 1, 15, 60, 10)
    inputTbox8 = TextBoxObj(winsAppBlock, "", 1, 16, 60, 10)
    inputTbox9 = TextBoxObj(winsAppBlock, "", 1, 17, 60, 10)

    # for the log scan & print result in the main console
    ButtonObj(winsAppBlock, "Scan", 3, 19 , click4ScanBBLog)


    titleBar4 = LableObj(winsAppBlock, "Scan Log Result", 0, 19)
    mainTextBox = ScTextBoxObj(winsAppBlock, 0, 20, 140, 30, 20)







    winsAppBlock.mainloop()
