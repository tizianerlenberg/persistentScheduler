#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2022 Tizian Erlenberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import time
import os
import json
import threading
import queue
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

def runFuntion(taskQueue, resultQueue):
    task= taskQueue.get()
    task['function'](*task['args'])
    resultQueue.put(task['name'])

class Scheduler:
    def __init__(self, file=Path(), fileUpdateInterval=1):
        self.dict= {}
        self.fileDict= {}
        self.fileUpdateInterval= fileUpdateInterval
        self.fileUpdateIntervalCursor= 0
        self.threadingDispatcher = {}
        self.threadingCompleted = {}
        self.runningThreads = {}

        if isinstance(file, str):
            self.file= Path(file)
        else:
            self.file= file

        if not os.path.exists(self.file):
            with open(self.file, "w") as myFile:
                myFile.write(json.dumps(self.fileDict))

        with open(self.file, "r") as myFile:
            content= myFile.read()
            if content != "":
                self.fileDict = json.loads(content)
            else:
                self.fileDict = {}
            for key in self.fileDict.keys():
                self.fileDict[key]["last"]= strToTime(self.fileDict[key]["last"])

    def updateFile(self):
        if self.file != Path():
            with open(self.file, "w") as myFile:
                self.fileDict= {}
                for key in self.dict.keys():
                    self.fileDict[key]= {}
                    self.fileDict[key]["last"]= timeToStr(self.dict[key]["last"])
                myFile.write(json.dumps(self.fileDict))
        else:
            raise Exception("File not specified in Constructor")

    def addTask(self, name, interval, function, group="", last=getTime(), args=[]):
        if name in self.dict.keys():
            raise Exception("Taskname is already in use, choose differnt name")
        if group == "":
            group = name
        self.dict[name]= {"interval": interval, "last": last, "function": function, "group": group, "args": args}
        self.threadingDispatcher[group]= queue.Queue()
        self.threadingCompleted[group]= queue.Queue()
        self.threadingCompleted[group].put(name)
    def addTaskIfNotExists(self, name, interval, function, group="", args=[]):
        if not (name in self.fileDict.keys()):
            self.addTask(name, interval, function, group=group)
        else:
            self.addTask(name, interval, function, last=self.fileDict[name]['last'], group=group, args=args)
    def removeTask(self, name):
        self.dict.pop(name)
    def runPending(self):
        for key in self.dict.keys():
            if (getTime() - self.dict[key]["last"]) > (self.dict[key]["interval"]):
                currentDispQueue= self.threadingDispatcher[self.dict[key]['group']]
                currentCompQueue= self.threadingCompleted[self.dict[key]['group']]
                if currentCompQueue.qsize() > 0:
                    completedTask = currentCompQueue.get()
                    self.dict[completedTask]["last"]= getTime()
                    currentDispQueue.put({'name': key, 'function': self.dict[key]['function'], 'args': self.dict[key]['args']})
                    self.runningThreads[self.dict[key]['group']] = threading.Thread(target=runFuntion, args=(currentDispQueue, currentCompQueue,))
                    self.runningThreads[self.dict[key]['group']].start()
    def runPendingAndUpdateFile(self, fileUpdateInterval=0):
        if fileUpdateInterval > 0:
            self.fileUpdateInterval= fileUpdateInterval
        for value in range(self.fileUpdateIntervalCursor, self.fileUpdateInterval):
            self.fileUpdateIntervalCursor += 1
            self.runPending()
            return
        self.fileUpdateIntervalCursor= 0
        self.runPending()
        self.updateFile()

def hello(input):
    print(input)

def main():
    test= Scheduler(file="test.json", fileUpdateInterval=5)
    test.addTaskIfNotExists("task1", datetime.timedelta(seconds=1), hello, group="task1", args=["task1"])
    test.addTaskIfNotExists("task2", datetime.timedelta(seconds=4), hello, group="task2", args=["task2"])
    test.updateFile()
    while True:
        test.runPendingAndUpdateFile()
        time.sleep(1)

if __name__ == '__main__':
    main()
