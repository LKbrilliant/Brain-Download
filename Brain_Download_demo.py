#                  ____             _          ____                      __                __
#                 / __ )_________ _(_)___     / __ \____ _      ______  / /___  ____ _____/ /
#                / __  / ___/ __ `/ / __ \   / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  /
#               / /_/ / /  / /_/ / / / / /  / /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /
#              /_____/_/   \__,_/_/_/ /_/  /_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/
#
#   Version     :   0.9.0.201222
#   Code by     :   Anuradha Gunawardhana(LKBrilliant)
#   Date        :   2020.12.30
#   Description :   Record and save raw EEG data extracted from 5 channel Emotiv Insight headset while
#                   displaying images or playing audio clips of multiple object classes.
#                   Saved records contain... 
#
#   Requirements: > Emotiv Apps need to be installed
#                 > A lLicense which allow exporting raw EEG data
#                 > The 'License-Key' (To access the SDK using the license, a request application need to be submitted) 
#                 > 'Client-ID' and 'Secret' from a Cortex App which created at the Emotiv website
#                 > Internet Connection
#
#   Instructions: > Add the 'Client-ID', 'Secret' and the SDK access enabled 'License-key' to the credentials.py
#                 > To create a new project, add image or audio files into a new folder inside the 'Data' directory
#                 > [Name of the project folder] = [Project Name]
#                 > Naming format: Cat_01.jpg, Dog_006.png, Hello_001.wav, Hello_07.mp3 ...
#                 > Supported file types: jpg, png, wav, mp3
#                 > Start the Emotive app and connect the headset to the PC via Bluetooth
#                 > Run the `Brain Download` GUI and press the `start` button
#                 > Adjust the headset so that the Contact Quality is above 95%
#                 > If needed use Emotive App's Contact Quality window to visualize individual electrodes
#                 > Select a Project and enter the subject's name, then press `Start Recording`
#                 > The recording will automatically stop after a 'interval + interval * count' number of seconds
#                 > The data will be saved as .CSV inside the 'Records' folder under the subject's name
#                 > Record name: [projectName]_[interval]sx[count]_[DATE]-[TIME].csv
#                 > While recording press `Cancel` to terminate a recording, the recorded data will not be saved
#
#   Experiments   > Random image persentation
#                   > If needed change the data composition by changeing the image count
#                 > Random Audio playing              
#                 > Left-Right Arrow Images
#                   > This type of imagesets should contain multiple classes of arrows and a single center image named as 'Center_001.JPG'
#                   > The GUI recognized this project by the phrase 'Arrow' in the folder name
#                   > The center image will be shown before every image
#                 > Visual Q&A
#                   > This kind of image-set should contain images form multiple classes Eg. 10 classes
#                   > The GUI recognize this type of image-set by the phrase 'Q&A' in the folder name
#                   > GUI will add a '?' to every class name and generate a question list Eg.for 10 classes -> 10 questions
#                   > When showing an image, a  question is asked above the image to get a 'YES', 'NO' responce from the subject
#                   > For 10 classes the program can ask 1 'YES' responce question to 9 'NO' responce questions 
#                   > But Asking the correct and incorrect question probability is set to 50%
#
#   Limitations : > Projects of mixed audio and images does not support

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from playsound import playsound
from eegExport_demo import RecordThread
from os import listdir
from os.path import isfile, isdir, join
import sys
import random

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):    

        self.interval = 0
        self.files = []
        self.projectName = ""
        self.recordingState = False
        self.lastName = ""
        self.extention = ""
        self.audioProject = False
        self.count = 0
        self.comboTest = False
        self.directionalProj = False
        self.dirTempBool = True
        self.VQAProj = False
        self.centerImageName = 'Center_001.JPG'
        self.directionalProjName = "Arrow"
        self.VQAProjName = "Q&A"
        self.questions = []
    
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(920, 910)
        MainWindow.setStyleSheet("background-color: #212121;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lbl_class = QtWidgets.QLabel(self.centralwidget)
        self.lbl_class.setMinimumSize(QtCore.QSize(0, 0))
        self.lbl_class.setMaximumSize(QtCore.QSize(2000, 72))
        font = QtGui.QFont()
        # font.setFamily("Times New Roman")
        font.setFamily("Nirmala UI")
        font.setPointSize(28)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)

        self.lbl_class.setFont(font)
        self.lbl_class.setStyleSheet("color: #ffffff;")
        self.lbl_class.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_class.setObjectName("lbl_class")
        self.gridLayout_3.addWidget(self.lbl_class, 0, 0, 1, 6)

        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setMaximumSize(QtCore.QSize(2000, 2000))
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("UI_graphics/brain_download.png"))
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.gridLayout_3.addWidget(self.image, 1, 0, 1, 6)

        self.btn_main = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_main.sizePolicy().hasHeightForWidth())
        self.btn_main.setSizePolicy(sizePolicy)
        self.btn_main.setMaximumSize(QtCore.QSize(200, 100))
        self.btn_main.setMinimumSize(QtCore.QSize(170, 50))
        self.btn_main.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_main.setStyleSheet(open("style_sheets/button_start.qss","r").read())
        self.btn_main.setObjectName("btn_main")
        self.btn_main.clicked.connect(self.buttonPress)
        self.gridLayout_3.addWidget(self.btn_main, 2, 5, 2, 1)

        self.lbl_status = QtWidgets.QLabel(self.centralwidget)
        self.lbl_status.setMaximumSize(QtCore.QSize(2000, 25))
        self.lbl_status.setStyleSheet("color: #505050;")
        self.lbl_status.setObjectName("lbl_status")
        self.gridLayout_3.addWidget(self.lbl_status, 3, 0, 1, 1)
        
        self.lbl_contactQuality = QtWidgets.QLabel(self.centralwidget)
        self.lbl_contactQuality.setMaximumSize(QtCore.QSize(2000, 25))
        self.lbl_contactQuality.setStyleSheet("color: #505050;")
        self.lbl_contactQuality.setObjectName("lbl_contactQuality")
        self.gridLayout_3.addWidget(self.lbl_contactQuality, 2, 0, 1, 1)
        
        self.txt_subjectName = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_subjectName.setMinimumSize(QtCore.QSize(100, 0))
        self.txt_subjectName.setMaximumSize(QtCore.QSize(150, 25))
        self.txt_subjectName.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.txt_subjectName.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
        self.txt_subjectName.setText("")
        self.txt_subjectName.setMaxLength(15)
        self.txt_subjectName.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_subjectName.setDragEnabled(False)
        self.txt_subjectName.setObjectName("txt_subjectName")
        self.gridLayout_3.addWidget(self.txt_subjectName, 2, 4, 1, 1)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMaximumSize(QtCore.QSize(150, 25))
        self.comboBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.comboBox.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setStyleSheet(open("style_sheets/comboBox_default.qss","r").read())
        self.comboBox.setFrame(True)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.currentIndexChanged.connect(self.comboChanged)
        self.gridLayout_3.addWidget(self.comboBox, 3, 4, 1, 1)

        self.lbl_projectName = QtWidgets.QLabel(self.centralwidget)
        self.lbl_projectName.setMaximumSize(QtCore.QSize(120, 25))
        self.lbl_projectName.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_projectName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_projectName.setObjectName("lbl_projectName")
        self.gridLayout_3.addWidget(self.lbl_projectName, 3, 3, 1, 1)

        self.lbl_subjectName = QtWidgets.QLabel(self.centralwidget)
        self.lbl_subjectName.setMaximumSize(QtCore.QSize(100, 25))
        self.lbl_subjectName.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_subjectName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_subjectName.setObjectName("lbl_subjectName")
        self.gridLayout_3.addWidget(self.lbl_subjectName, 2, 3, 1, 1)

        self.txt_interval = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_interval.setMinimumSize(QtCore.QSize(0, 0))
        self.txt_interval.setMaximumSize(QtCore.QSize(60, 25))
        self.txt_interval.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.txt_interval.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
        self.txt_interval.setMaxLength(3)
        self.txt_interval.setFrame(True)
        self.txt_interval.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_interval.setDragEnabled(False)
        self.txt_interval.setObjectName("txt_interval")
        self.txt_interval.setToolTip('Period between two files')  
        self.gridLayout_3.addWidget(self.txt_interval, 2, 2, 1, 1)

        self.lbl_interval = QtWidgets.QLabel(self.centralwidget)
        self.lbl_interval.setMinimumSize(QtCore.QSize(120, 0))
        self.lbl_interval.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_interval.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_interval.setObjectName("lbl_interval")
        self.gridLayout_3.addWidget(self.lbl_interval, 2, 1, 1, 1)

        self.txt_count= QtWidgets.QLineEdit(self.centralwidget)
        self.txt_count.setMinimumSize(QtCore.QSize(0, 0))
        self.txt_count.setMaximumSize(QtCore.QSize(60, 25))
        self.txt_count.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.txt_count.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
        self.txt_count.setMaxLength(3)
        self.txt_count.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_count.setDragEnabled(False)
        self.txt_count.setObjectName("txt_count")
        self.txt_count.setToolTip('Number of files for a recording')
        self.gridLayout_3.addWidget(self.txt_count, 3, 2, 1, 1)

        self.lbl_count= QtWidgets.QLabel(self.centralwidget)
        self.lbl_count.setMinimumSize(QtCore.QSize(120, 0))
        self.lbl_count.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_count.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_count.setObjectName("lbl_count")
        self.gridLayout_3.addWidget(self.lbl_count, 3, 1, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.record = RecordThread()                # Initialize the Recording thread
        self.record.status.connect(self.threadMsgHandler)
        self.record.contactQuality.connect(self.CQHandler)
        self.menuVisibility('all',False)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Brain Download"))
        MainWindow.setWindowIcon(QtGui.QIcon('UI_graphics/logo.png'))
        self.lbl_class.setText(_translate("MainWindow", ""))
        self.btn_main.setText(_translate("MainWindow", "Start"))
        self.lbl_status.setText(_translate("MainWindow", "Status:"))
        self.lbl_contactQuality.setText(_translate("MainWindow", ""))
        self.lbl_subjectName.setText(_translate("MainWindow", "Subject Name: "))
        self.lbl_projectName.setText(_translate("MainWindow", "Project Name: "))
        self.txt_interval.setText(_translate("MainWindow", "2"))
        self.lbl_interval.setText(_translate("MainWindow", "Interval(s):"))
        self.txt_count.setText(_translate("MainWindow", "20"))
        self.lbl_count.setText(_translate("MainWindow", "Count:"))
        

    def threadMsgHandler(self,result):
        self.statusUpdate(result)
        if result == "Initializing":
            self.btn_main.setText("Initializing")
            self.btn_main.setStyleSheet(open("style_sheets/button_initializing.qss","r").read())

        elif result == "Initialization: Successful":
            self.btn_main.setText("Start Recording")
            self.btn_main.setStyleSheet(open("style_sheets/button_startRecording.qss","r").read())
            self.menuVisibility('all',True)
            self.comboBoxUpdated = self.updateComboBox()
            
        elif result == "Initialization: Failed":
            self.btn_main.setText("Try again")
            self.btn_main.setStyleSheet(open("style_sheets/button_start.qss","r").read())
            
        elif result == "Recording":
            self.btn_main.setText("Cancel")
            self.btn_main.setStyleSheet(open("style_sheets/button_stop.qss","r").read())
            self.recordingState = True
            self.sequencing()

    def CQHandler(self,result):
        self.lbl_contactQuality.setText("Contact Quality: {}%".format(result))

    def buttonPress(self):
        btn_text = self.btn_main.text()
        if btn_text == "Start":    
            self.record.start()                     # start the thread

        elif btn_text == "Cancel":
            self.record.saving = False              # Cancel and don't save the recording
            self.stopRecording()          
        
        elif btn_text == "Start Recording":
            self.record.contactTest = False
            if self.prerequisiteTest():
                self.interval = float(self.txt_interval.text())
                self.record.interval = self.interval
                self.count = int(self.txt_count.text())
                self.record.count = self.count
                self.record.audioProject = self.audioProject
                                    
                self.getFileList()
                self.record.startRecording = True   # start headset data collection
                self.record.start()                 # start the thread
                self.menuVisibility('all',False)
            
        elif btn_text == "Try again":
            self.btn_main.setStyleSheet(open("style_sheets/button_initializing.qss","r").read())
            self.btn_main.setText("Initializing")
            self.record.start()                     # start the thread
    
    def stopRecording(self):
        self.btn_main.setStyleSheet(open("style_sheets/button_startRecording.qss","r").read())
        self.btn_main.setText("Start Recording")
        self.recordingState = False                 # Stop sequencing of images
        self.record.startRecording = False          # stop headset data collection
        self.menuVisibility('all',True)
        self.record.marker = ""
        self.image.setPixmap(QtGui.QPixmap("UI_graphics/brain_download.png"))
        self.lbl_class.setText("")
        self.record.contactTest = True
        QtTest.QTest.qWait(2000)                    # delay some time before starting the contact quality test again
        self.record.start()
    
    def sequencing(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFile)
        self.timer.start(self.interval*1000)

    def nextFile(self):
        if self.recordingState:
            fileName = random.choice(self.files)
            while fileName == self.lastName:                    # avoid consecutive same file selection
                fileName = random.choice(self.files)
            self.lastName = fileName
            filePath = "Data/{}/{}".format(self.projectName,fileName)      
            self.record.tick = not self.record.tick
            className = fileName.split('_')[0]
            if not self.VQAProj and not self.directionalProj: self.record.marker = className # Insert markers only if the projects are not 'VQ&A' or 'Arrow'
            if self.count != 0:
                if self.audioProject: playsound(filePath)       # When Audio project selected
                elif self.directionalProj:                      # If the directional(Arrow) project was selected
                    if self.dirTempBool:
                        self.record.marker = 'Center'
                        centerImgPath = "Data/{}/{}".format(self.projectName,self.centerImageName)
                        self.dirTempBool = False
                        self.image.setPixmap(QtGui.QPixmap(centerImgPath))
                    else: 
                        self.record.marker = className
                        self.image.setPixmap(QtGui.QPixmap(filePath))
                        self.dirTempBool = True
                elif self.VQAProj:
                    wrong = [x for x in self.questions if not className in x]              # Get what can be ask as a wrong question
                    q = random.choice(wrong) if random.choice([1,0]) else className+'?'    # Get the correct probability for asking correct and incorrect question
                    self.lbl_class.setText(q)                                              # Ask the chosen question
                    self.image.setPixmap(QtGui.QPixmap(filePath))
                    self.record.marker = 'YES' if className in q else 'NO'
                else: self.image.setPixmap(QtGui.QPixmap(filePath))
            else:
                self.record.saving = True                       # Stop and save the recording
                self.stopRecording()
            self.count -= 1

    def statusUpdate(self,message):
        self.lbl_status.setText("Status: {}".format(message))

    def isFloat(self,num):
        try :  
            float(num) 
            return True
        except : 
            return False
    
    def prerequisiteTest(self):

        if self.txt_subjectName.text() != "" and self.txt_interval.text() != "" and self.txt_count.text() != "" and self.comboBoxUpdated:
            self.txt_subjectName.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
            self.txt_interval.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
            self.txt_count.setStyleSheet(open("style_sheets/lineEdit_default.qss","r").read())
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_default.qss","r").read())
            self.record.subjectName = self.txt_subjectName.text()
            check = True

        if self.txt_subjectName.text() == "":
            self.statusUpdate("Error:Fill the required fields")
            self.txt_subjectName.setStyleSheet(open("style_sheets/lineEdit_warning.qss","r").read())
            check = False

        if not self.isFloat(self.txt_interval.text()):
            self.statusUpdate("Error:Fill the required fields")
            self.txt_interval.setStyleSheet(open("style_sheets/lineEdit_warning.qss","r").read())
            check = False

        if not(self.txt_count.text().isdigit()):
            self.statusUpdate("Error:Fill the required fields")
            self.txt_count.setStyleSheet(open("style_sheets/lineEdit_warning.qss","r").read())
            check = False

        if not self.comboBoxUpdated:
            self.statusUpdate("Error:Add project folders to the 'Data' directory")
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_warning.qss","r").read())
            check = False
        
        if not self.comboTest:
            self.statusUpdate("Error:Support extentions ['jpg','png','wav','mp3']")
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_warning.qss","r").read())
            check = False

        if check == True: return True
        else: return False

    def updateComboBox(self):
        path = "Data"
        dirs = listdir(path)
        if len(dirs) == 0:
            self.statusUpdate("Error:No Projects Found")
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_warning.qss","r").read())
            return False
        else:
            self.comboBox.addItems(dirs)
            return True
    
    def getFileList(self):
        path = "Data/{}".format(self.projectName)
        self.files = [f for f in listdir(path) if isfile(join(path, f))]
        justText = [i.split('_')[0] for i in self.files]    # Get just the text from all files names
        uniqueText = list(set(justText))                    # Get all unique names from the files
        uniqueText.sort()                                   # Sort to make the order always the same
        if self.VQAProj:
            self.record.classes = ['YES','NO']
            self.questions = ["{}{}".format(i,'?') for i in uniqueText]    # Add a question mark '?' at the end of each class name
        else: self.record.classes = uniqueText
    
    def menuVisibility(self,section,state):
        if section == 'all':
            self.lbl_subjectName.setVisible(state)
            self.lbl_interval.setVisible(state)
            self.lbl_count.setVisible(state)
            self.lbl_projectName.setVisible(state)
            self.txt_subjectName.setVisible(state)
            self.txt_interval.setVisible(state)
            self.txt_count.setVisible(state)
            self.comboBox.setVisible(state)
        if section == 'part':
            self.lbl_interval.setVisible(state)
            self.txt_interval.setVisible(state)
            self.lbl_count.setVisible(state)
            self.txt_count.setVisible(state)
    
    def comboChanged(self):
        self.directionalProj = False
        self.VQAProj = False
        self.projectName = self.comboBox.currentText()
        self.record.projectName = self.comboBox.currentText()

        path = "Data/{}".format(self.projectName)
        self.files = [f for f in listdir(path) if isfile(join(path, f))]
        extensions = [i.split('.')[1] for i in self.files]      # Get just the extentions from all files names
        uniqueExt = [x.lower() for x in list(set(extensions))]  # list of all unique extentions in lower case

        self.statusUpdate("Initialization: Successful")
        self.comboBox.setStyleSheet(open("style_sheets/comboBox_default.qss","r").read())
        self.menuVisibility('all',True)

        if len(uniqueExt)==0:
            self.statusUpdate("Error:Empty Folder")
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_warning.qss","r").read())
            self.menuVisibility('part',False)
            self.comboTest = False
        elif set(uniqueExt) <= set(['mp3','wav']):              # check if uniqueExt is a subset of ['mp3,'wav']
            self.audioProject = True
            self.comboTest = True
        elif set(uniqueExt) <= set(['jpg','png','txt']):
            self.audioProject = False
            self.comboTest = True
            if self.directionalProjName in self.projectName: 
                self.directionalProj = True
                self.files.remove(self.centerImageName)         # Remove the Center dot image from the arrow list
            if self.VQAProjName in self.projectName: 
                self.VQAProj = True
        else:
            self.statusUpdate("Error:No Audio/Image Files")
            self.comboBox.setStyleSheet(open("style_sheets/comboBox_warning.qss","r").read())
            self.menuVisibility('part',False)
            self.comboTest = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())