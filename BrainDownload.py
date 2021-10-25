#                  ____             _          ____                      __                __
#                 / __ )_________ _(_)___     / __ \____ _      ______  / /___  ____ _____/ /
#                / __  / ___/ __ `/ / __ \   / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  / 
#               / /_/ / /  / /_/ / / / / /  / /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /  
#              /_____/_/   \__,_/_/_/ /_/  /_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/ 
#
#   Version     :   0.6.2.200831
#   Code by     :   Anuradha Gunawardhana(LKBrilliant)
#   Date        :   2020.08.31
#   Description :   Record and save EEG data extracted from 5 channel Emotiv Insight headset while
#                   displaying images of multiple object classes
#            
#   Requirements: > Emotiv Apps need to be installed
#                 > A license which allow exporting EEG data
#                 > Client-ID and Secret from a Cortex App which created at the Emotiv website
#                 > An API-Key (by applying for the API access)
#                 > Internet Connection
# 
#   Instructions: > Add the Client-ID, Secret and License-key to the credentials.py 
#                 > Add images to a new folder inside the 'Images' directory to create a new project
#                 > The name of the folder will be recognize as the Project Name 
#                 > Image name format: Cat_01.jpg, Dog_02.jpg ...
#                 > If needed change the `imgInterval` and `recordDuration`
#                 > Start the Emotive app and connect the headset to the PC via Bluetooth
#                 > Run the `Brain Download` GUI and press the `start` button
#                 > Adjust the headset so that the Contact Quality is above 95%
#                 > If needed use Emotive App's Contact Quality window to visualize individual electrodes
#                 > Select a project and enter the subject's name, then press `Start Recording`
#                 > The recording will automatically end after the preset `recordDuration` time
#                 > The data will be saved as .CSV inside the 'Records' folder under the subject's name
#                 > Record name: [projectName]_[imgInterval]s-[recordDuration]s_[DATE]-[TIME].csv
#                 > Press `Cancel` to cancel a recording, the recorded data will not be saved
#
#   Limitations : > Image-interval and record-duration time cannot change within the GUI

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from eegExport import RecordThread
from os import listdir
from os.path import isfile, isdir, join
import sys
import random

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        #------------ User Defined values -------------#
        self.imgInterval = 2000
        self.recordDuration = 30000
        #----------------------------------------------#

        self.files = []
        self.projectName = ""
        self.recordingState = False
        self.lastName = ""

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(920, 910)
        MainWindow.setStyleSheet("background-color: #212121;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lbl_imageClass = QtWidgets.QLabel(self.centralwidget)
        self.lbl_imageClass.setMinimumSize(QtCore.QSize(0, 0))
        self.lbl_imageClass.setMaximumSize(QtCore.QSize(2000, 72))

        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(28)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)

        self.lbl_imageClass.setFont(font)
        self.lbl_imageClass.setStyleSheet("color: #ffffff;")
        self.lbl_imageClass.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_imageClass.setObjectName("lbl_imageClass")
        self.gridLayout_3.addWidget(self.lbl_imageClass, 0, 0, 1, 4)

        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setMaximumSize(QtCore.QSize(2000, 2000))
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("UI_graphics\\brain_download.png"))
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.gridLayout_3.addWidget(self.image, 1, 0, 1, 4)

        self.btn_main = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_main.sizePolicy().hasHeightForWidth())
        self.btn_main.setSizePolicy(sizePolicy)
        self.btn_main.setMaximumSize(QtCore.QSize(200, 100))
        self.btn_main.setMinimumSize(QtCore.QSize(170, 50))
        self.btn_main.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_main.setStyleSheet(open("style_sheets\\button_start.qss","r").read())
        self.btn_main.setObjectName("btn_main")
        self.btn_main.clicked.connect(self.buttonPress)
        self.gridLayout_3.addWidget(self.btn_main, 2, 3, 2, 1)

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

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMaximumSize(QtCore.QSize(150, 25))
        self.comboBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.comboBox.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setStyleSheet(open("style_sheets\\comboBox_default.qss","r").read())
        self.comboBox.setFrame(True)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.currentIndexChanged.connect(self.comboChanged)
        self.gridLayout_3.addWidget(self.comboBox, 3, 2, 1, 1)
        
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setMaximumSize(QtCore.QSize(150, 25))
        self.lineEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEdit.setStyleSheet(open("style_sheets\\lineEdit_default.qss","r").read())
        self.lineEdit.setText("")
        self.lineEdit.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit.setDragEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_3.addWidget(self.lineEdit, 2, 2, 1, 1)

        self.lbl_subjectName = QtWidgets.QLabel(self.centralwidget)
        self.lbl_subjectName.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_subjectName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_subjectName.setObjectName("lbl_subjectName")
        self.gridLayout_3.addWidget(self.lbl_subjectName, 2, 1, 1, 1)

        self.lbl_projectName = QtWidgets.QLabel(self.centralwidget)
        self.lbl_projectName.setStyleSheet("color: rgb(80,80, 80);")
        self.lbl_projectName.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_projectName.setObjectName("lbl_projectName")
        self.gridLayout_3.addWidget(self.lbl_projectName, 3, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.record = RecordThread()                # Initialize the Recording thread
        self.record.status.connect(self.threadMsgHandler)
        self.record.contactQuality.connect(self.CQHandler)
        self.subjectProjectVisibility(False)
        self.record.recordDuration = self.recordDuration
        self.record.imgInterval = self.imgInterval

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Brain Download"))
        MainWindow.setWindowIcon(QtGui.QIcon('UI_graphics\\logo.png'))
        self.lbl_imageClass.setText(_translate("MainWindow", ""))
        self.btn_main.setText(_translate("MainWindow", "Start"))
        self.lbl_status.setText(_translate("MainWindow", "Status:"))
        self.lbl_contactQuality.setText(_translate("MainWindow", ""))
        self.lbl_subjectName.setText(_translate("MainWindow", "Subject Name: "))
        self.lbl_projectName.setText(_translate("MainWindow", "Project Name: "))

    def threadMsgHandler(self,result):
        self.statusUpdate(result)
        if result == "Initializing":
            self.btn_main.setText("Initializing")
            self.btn_main.setStyleSheet(open("style_sheets\\button_initializing.qss","r").read())

        elif result == "Initialization: Successful":
            self.btn_main.setText("Start Recording")
            self.btn_main.setStyleSheet(open("style_sheets\\button_startRecording.qss","r").read())
            self.subjectProjectVisibility(True)
            self.comboBoxUpdated = self.updateComboBox()
            
        elif result == "Initialization: Failed":
            self.btn_main.setText("Try again")
            self.btn_main.setStyleSheet(open("style_sheets\\button_start.qss","r").read())
            
        elif result == "Recording":
            self.btn_main.setText("Cancel")
            self.btn_main.setStyleSheet(open("style_sheets\\button_stop.qss","r").read())
            self.recordingState = True
            self.imgSequencing()
            self.recordTimer()

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
            if self.subjectProjectTest():
                self.projectName = self.comboBox.currentText()
                self.record.projectName = self.comboBox.currentText()
                self.getImageList()
                self.record.startRecording = True   # start headset data collection
                self.record.start()                 # start the thread
                self.subjectProjectVisibility(False)
            
        elif btn_text == "Try again":
            self.btn_main.setStyleSheet(open("style_sheets\\button_initializing.qss","r").read())
            self.btn_main.setText("Initializing")
            self.record.start()                     # start the thread
    
    def stopRecording(self):
        self.btn_main.setStyleSheet(open("style_sheets\\button_startRecording.qss","r").read())
        self.btn_main.setText("Start Recording")
        self.recordingState = False                 # Stop sequencing of images
        self.record.startRecording = False          # stop headset data collection
        self.subjectProjectVisibility(True)
        self.record.marker = ""
        self.image.setPixmap(QtGui.QPixmap("UI_graphics\\brain_download.png"))
        self.lbl_imageClass.setText("")
        self.record.contactTest = True
        QtTest.QTest.qWait(2000)                    # delay some time before starting the contact quality test again
        self.record.start()

    def recordTimer(self):
        self.timer_1 = QtCore.QTimer()
        self.timer_1.timeout.connect(self.recordTimerHandler)
        self.timer_1.start(self.recordDuration)

    def recordTimerHandler(self):
        if self.recordingState:
            self.record.saving = True               # Stop and save the recording
            self.stopRecording()
    
    def imgSequencing(self):
        self.timer_2 = QtCore.QTimer()
        self.timer_2.timeout.connect(self.updateImage)
        self.timer_2.start(self.imgInterval)

    def updateImage(self):
        if self.recordingState:
            imageName = random.choice(self.files)
            while imageName == self.lastName:               # avoid consecutive same image selection
                imageName = random.choice(self.files)
            self.lastName = imageName
            imagePath = "Images\\{}\\{}".format(self.projectName,imageName)      
            self.record.tick = not self.record.tick
            self.record.marker= imageName.split('_')[0]     # Insert markers
            self.image.setPixmap(QtGui.QPixmap(imagePath))
            self.lbl_imageClass.setText(imageName.split('_')[0])

    def statusUpdate(self,message):
        self.lbl_status.setText("Status: {}".format(message))

    def subjectProjectTest(self):
        if self.lineEdit.text() == "":
            self.statusUpdate("Error:Fill the Subject Name")
            self.lineEdit.setStyleSheet(open("style_sheets\\lineEdit_warning.qss","r").read())
            return False

        elif self.lineEdit.text() == "" and not self.comboBoxUpdated:
            self.statusUpdate("Error:Add project folders to the 'Images' directory")
            self.lineEdit.setStyleSheet(open("style_sheets\\lineEdit_warning.qss","r").read())
            return False

        elif self.lineEdit.text() != "" and not self.comboBoxUpdated:
            self.statusUpdate("Error:Add project folders to the 'Images' directory")
            self.lineEdit.setStyleSheet(open("style_sheets\\lineEdit_default.qss","r").read())
            return False

        elif self.lineEdit.text() != "" and self.comboBoxUpdated:
            self.lineEdit.setStyleSheet(open("style_sheets\\lineEdit_default.qss","r").read())
            self.record.subjectName = self.lineEdit.text()
            return True

    def updateComboBox(self):
        path = "Images"
        dirs = listdir(path)
        if len(dirs) == 0:
            self.statusUpdate("Error:No Projects Found")
            self.comboBox.setStyleSheet(open("style_sheets\\comboBox_warning.qss","r").read())
            return False
        else:
            self.comboBox.addItems(dirs)
            return True
    
    def getImageList(self):
        path = "Images\\{}".format(self.projectName)
        self.files = [f for f in listdir(path) if isfile(join(path, f))]
        justText = [i.split('_')[0] for i in self.files]    # Get just the text from all files names
        uniqueText = list(set(justText))                    # Get all unique names from the files
        uniqueText.sort()                                   # Sort to make the order always the same
        self.record.classes = uniqueText
    
    def subjectProjectVisibility(self,state):
        self.lbl_subjectName.setVisible(state)
        self.lbl_projectName.setVisible(state)
        self.lineEdit.setVisible(state)
        self.comboBox.setVisible(state)
    
    def comboChanged(self):
        self.projectName = self.comboBox.currentText()
        self.record.projectName = self.comboBox.currentText()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())