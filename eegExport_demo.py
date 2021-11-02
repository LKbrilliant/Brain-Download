from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import datetime
import time

class RecordThread(QThread):
    status = pyqtSignal('PyQt_PyObject')
    contactQuality = pyqtSignal("PyQt_PyObject")

    def __init__(self):
        QThread.__init__(self)

        self.stopRecording = False
        self.startRecording = False
        self.contactTest = True
        self.initialized = False
        self.saving = False
        self.interval = 0
        self.subjectName = ""
        self.projectName = ""
        self.marker = ""
        self.tick = 0
        self.classes = []
        self.CQuality  = 0
        self.audioProject = False
        self.count = 0

    def run(self):
        flag = False
        if self.initialized == False:
            self.status.emit("Initializing")
            time.sleep(3)
            self.status.emit("Initialization: Successful")
            self.initialized = True
            
        if self.contactTest:
            self.getContactQuality()

        if self.startRecording:
            self.status.emit("Recording")
            data=[]
            while self.startRecording:
                flag = True
            self.status.emit("Recording Canceled")
            if self.saving:
                savedFileName = self.saveRecord(data)
                self.status.emit("Record saved: '{}'".format(savedFileName))

    def getContactQuality(self):
        self.contactQuality.emit("100")

    def saveRecord(self,dataFile):
        finalDir = "Records\{}".format(self.subjectName)
        now = datetime.datetime.now()
        timestamp = now.strftime("%y%m%d-%H%M%S")
        newFileName = "{}\{}_{}sx{}_{}.csv".format(finalDir,self.projectName,self.interval,self.count,timestamp)
        return newFileName