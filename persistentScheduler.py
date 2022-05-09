#!/usr/bin/env python3

"""
TODO:
- implement threading with groups
"""

import datetime
import time
import os
import json
from pathlib import Path, PurePosixPath
from random import randint

DISPATCHER = {}
COMPLETED = {}

def getTime():
    return datetime.datetime.now()

def timeToStr(time):
    return time.isoformat()

def strToTime(input):
    return datetime.datetime.fromisoformat(input)

def deltaToStr(delta):
    zerodate= datetime.datetime(1, 1, 1)
    return timeToStr((zerodate + delta))

def strToDelta(input):
    zerodate= datetime.datetime(1, 1, 1)
    return strToTime(input) - zerodate

class Scheduler:
    def __init__(self, file=Path(), fileUpdateInterval=1):
        self.dict= {}
        self.fileDict= {}
        self.functions= {}
        self.fileUpdateInterval= fileUpdateInterval
        self.fileUpdateIntervalCursor= 0

        if isinstance(file, str):
            self.file= Path(file)
        else:
            self.file= file

        if not os.path.exists(self.file):
            with open(self.file, "w") as myFile:
                myFile.write(json.dumps(self.fileDict))

        with open(self.file, "r") as myFile:
            self.fileDict = json.loads(myFile.read())
    def updateFile(self):
        if self.file != Path():
            with open(self.file, "w") as myFile:
                self.fileDict= self.dict
                myFile.write(json.dumps(self.fileDict))
        else:
            raise Exception("File not specified in Constructor")
    def addTask(self, name, interval, function, group="", last=timeToStr(getTime())):
        self.dict[name]= {"interval": deltaToStr(interval), "last": last, "function": function.__name__}
        self.functions[function.__name__]= function
    def addTaskIfNotExists(self, name, interval, function, group=""):
        if not (name in self.fileDict.keys()):
            self.addTask(name, interval, function)
        else:
            self.addTask(name, interval, function, last=self.fileDict[name]['last'])
    def removeTask(self, name):
        self.dict.pop(name)
    def runPending(self):
        for d in self.dict:
            if (getTime() - strToTime(self.dict[d]["last"])) > strToDelta(self.dict[d]["interval"]):
                print(f"doing {d}")
                self.functions[self.dict[d]["function"]]()
                self.dict[d]["last"]= timeToStr(datetime.datetime.now())
    def runPendingAndUpdateFile(self):
        for value in range(self.fileUpdateIntervalCursor, self.fileUpdateInterval):
            self.fileUpdateIntervalCursor += 1
            self.runPending()
            return
        self.fileUpdateIntervalCursor= 0
        self.runPending()
        self.updateFile()

def hello():
    print("hello")

def main():
    test= Scheduler(file="test.json")
    test.addTaskIfNotExists("task1", datetime.timedelta(seconds=20), hello)
    test.updateFile()
    while True:
        test.runPendingAndUpdateFile()
        time.sleep(1)

if __name__ == '__main__':
    main()
