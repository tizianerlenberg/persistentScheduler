#!/usr/bin/env python3

"""
TODO:
- implement adding functions to task
- implement threding with groups
"""

import datetime
import time
import os
import json
from pathlib import Path, PurePosixPath
from random import randint

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
    def __init__(self, file=Path()):
        self.dict= {}

        if isinstance(file, str):
            self.file= Path(file)
        else:
            self.file= file

        if not os.path.exists(self.file):
            with open(self.file, "w") as myFile:
                myFile.write(json.dumps(self.dict))

        with open(self.file, "r") as myFile:
            self.dict = json.loads(myFile.read())

    def addTask(self, name, interval):
        self.dict[name]= {"interval": deltaToStr(interval), "last": timeToStr(getTime())}
    def addTaskIfNotExists(self, name, interval):
        if not (name in self.dict.keys()):
            self.addTask(name, interval)
    def removeTask(self, name):
        self.dict.pop(name)
    def runPending(self):
        for d in self.dict:
            if (getTime() - strToTime(self.dict[d]["last"])) > strToDelta(self.dict[d]["interval"]):
                print(f"doing {d}")
                self.dict[d]["last"]= timeToStr(datetime.datetime.now())
    def updateFile(self):
        if self.file != Path():
            with open(self.file, "w") as myFile:
                myFile.write(json.dumps(self.dict))
        else:
            raise Exception("File not specified in Constructor")

def main():
    test= Scheduler(file="test.json")
    test.addTaskIfNotExists("task1", datetime.timedelta(seconds=2))
    while True:
        test.runPending()
        test.updateFile()
        time.sleep(1)

if __name__ == '__main__':
    main()
