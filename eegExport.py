from PyQt5.QtCore import QThread, pyqtSignal
from cortex import Cortex
import credentials
import os
import numpy as np
import json
import datetime

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
            self.headset = Cortex(credentials.user, debug_mode=False)
            self.status.emit("Initializing")
            try:
                self.headset.do_prepare_steps()
                self.headset.sub_request(["eeg","dev"])
                self.status.emit("Initialization: Successful")
                self.initialized = True
            except:
                self.status.emit("Initialization: Failed")
                self.initialized = False

        if self.contactTest:
            self.getContactQuality()

        if self.startRecording:
            self.status.emit("Recording")
            data=[]
            while self.startRecording:
                received = json.loads(self.headset.ws.recv())
                if flag and "eeg" in received and self.marker != "":    # Skip the first line for eeg not recording the empty markers
                    received["eeg"].pop(1)                              # remove the "INTERPOLATED" column
                    p = received["eeg"][:6]                             # EEG stream
                    p.append(self.classes.index(self.marker))           # Add markers
                    p.append(self.tick)                                 # Add the ticks
                    p.append(self.CQuality)                             # Add contact quality
                    data.append(p)
                if flag and "dev" in received:
                    k = received['dev'][2][5]
                    self.CQuality = int(k)
                    self.contactQuality.emit(str(k))
                flag = True
            self.status.emit("Recording Canceled")
            if self.saving:
                savedFileName = self.saveRecord(data)
                self.status.emit("Record saved: '{}'".format(savedFileName))

    def getContactQuality(self):
        while self.contactTest:
            received = json.loads(self.headset.ws.recv())
            if "dev" in received:
                k = received['dev'][2][5]
                self.CQuality = int(k)
                self.contactQuality.emit(str(k))

    def saveRecord(self,dataFile):
        finalDir = "Records\{}".format(self.subjectName)
        if not os.path.isdir(finalDir):
            os.mkdir(finalDir)
        now = datetime.datetime.now()
        timestamp = now.strftime("%y%m%d-%H%M%S")
        newFileName = "{}\{}_{}sx{}_{}.csv".format(finalDir,self.projectName,self.interval,self.count,timestamp)
        s = str(self.classes).replace(', ',',')       # Remove space after the commas for easy data analysis 
        np.savetxt(newFileName,dataFile,delimiter =", ",header="COUNTER, AF3, T7, Pz, T8, AF4, MARKERS{}, TICK, ContactQuality".format(s), comments='')
        return newFileName