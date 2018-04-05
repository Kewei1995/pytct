#! /usr/bin/env python

#reference:
#Luis Ardila 	leardilap@unal.edu.co 	22/03/15

#Liejian Chen   

import sys,time
import numpy
from PyQt5 import QtGui, QtCore, uic, QtWidgets

tctEnable = True
if tctEnable:
    import pymotor
    import thread
    import MDO3034Control
    import VitualDevice as vitual_dev

testpass = False



class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        ################################################
        #initialize the device information,search usable device
        self.EmumDevice()

        self.uiFile = "GUI/XYZWidget.ui"
        self.ui = uic.loadUi(self.uiFile)
        self.Title = "TCT Control"
        ##############################################################
        self.timer = QtCore.QTimer()
       
        self.SetMotor()
        #self.SetSpeed()
        self.ui.Interface.addItems(MDO3034Control.ReadInterface())
            

        #Move
        self.ui.MoveButton.clicked.connect(lambda:self.ClickMove(int(self.ui.SetPosX.text()), int(self.ui.SetPosY.text()), int(self.ui.SetPosZ.text())))

        #Step move X
        self.ui.XPlus.clicked.connect(lambda:self.MoveStep("X",1,self.ui.StepMoveX.value()))
        self.ui.XMinus.clicked.connect(lambda:self.MoveStep("X",-1,self.ui.StepMoveX.value()))

        #Step move Y
        self.ui.YPlus.clicked.connect(lambda:self.MoveStep("Y",1,self.ui.StepMoveY.value()))
        self.ui.YMinus.clicked.connect(lambda:self.MoveStep("Y",-1,self.ui.StepMoveY.value()))

        #Step move Z
        self.ui.ZPlus.clicked.connect(lambda:self.MoveStep("Z",1,self.ui.StepMoveZ.value()))
        self.ui.ZMinus.clicked.connect(lambda:self.MoveStep("Z",-1,self.ui.StepMoveZ.value()))

        #Home
        self.ui.ResetPosX.clicked.connect(lambda:self.Home("X"))
        self.ui.ResetPosY.clicked.connect(lambda:self.Home("Y"))
        self.ui.ResetPosZ.clicked.connect(lambda:self.Home("Z"))

        #scan
        self.ui.ScanBut.clicked.connect(self.Scan)

        #Stop
        self.ui.StopBut.clicked.connect(self.Stop)
        self.ui.ScanStop.clicked.connect(self.ScanStop)

        #set motor
        self.ui.SetMotor.clicked.connect(self.SetMotor)

        #set speed
        self.ui.Set_Speed.clicked.connect(self.SetSpeed)

        #set folder
        self.ui.FolderSet.clicked.connect(self.SetFolder)

        #capture data
        self.ui.CaptureBut.clicked.connect(self.SaveData)

        #capture pause
        self.ui.CapturePause.clicked.connect(self.CapturePause)

        #Capture ready
        self.ui.ReadyBut.clicked.connect(self.Ready)

         # Var
        self.currentPosX = 0
        self.currentPosY = 0
        self.currentPosZ = 0

        #####################
        # Initializing Widget
        self.UpdateDesiredPos()
        self.ui.setWindowTitle(self.Title)
        self.timer.timeout.connect(self.UpdateDesiredPos)

       
        self.ui.show()

    def ClickMove(self,px,py,pz):
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 3
        self.new_thread.px = px
        self.new_thread.py = py
        self.new_thread.pz = pz
        self.new_thread.start()

    def MoveStep(self,motor,direction,steps):
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 4
        self.new_thread.mv = direction*steps
        if motor == "X":
            self.new_thread.motor = self.new_thread.laser_stage.Xaxis
        elif motor == "Y":
            self.new_thread.motor = self.new_thread.laser_stage.Yaxis
        elif motor == "Z":
            self.new_thread.motor = self.new_thread.laser_stage.Zaxis
        else:
            print("\n\n\nError!!!!!!!\n\n\n")
        self.new_thread.start()
    def Home(self,motor):
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 1
        if motor == "X":
            self.new_thread.motor = self.new_thread.laser_stage.Xaxis
        elif motor == "Y":
            self.new_thread.motor = self.new_thread.laser_stage.Yaxis
        elif motor == "Z":
            self.new_thread.motor = self.new_thread.laser_stage.Zaxis
        else:
            print("\n\n\nError!!!!!!!\n\n\n")
        self.new_thread.start()
    def Scan(self):
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 5
        self.new_thread.po = [self.ui.x0.value(),self.ui.y0.value(),self.ui.z0.value()]
        self.new_thread.dp = [self.ui.dx.value(),self.ui.dy.value(),self.ui.dz.value()]
        self.new_thread.Np = [self.ui.Nx.value(),self.ui.Ny.value(),self.ui.Nz.value()]
        self.new_thread.start()

    def SetMotor(self):
        self.setdevice = numpy.empty(3,dtype=object)
        self.setdevice[0] = self.device[self.ui.X_Motor_Num.value()-1]
        self.setdevice[1] = self.device[self.ui.Y_Motor_Num.value()-1]
        self.setdevice[2] = self.device[self.ui.Z_Motor_Num.value()-1]

    def SetSpeed(self):
        self.steps = numpy.empty(3,dtype=int)
        self.speed = numpy.empty(3,dtype=int)
        self.steps[0] = self.ui.Step_X.value()
        self.steps[1] = self.ui.Step_Y.value()
        self.steps[2] = self.ui.Step_Z.value()
        self.speed[0] = self.ui.Speed_X.value()
        self.speed[1] = self.ui.Speed_Y.value()
        self.speed[2] = self.ui.Speed_Z.value()
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 6
        self.new_thread.step = self.steps
        self.new_thread.speed = self.speed
        self.new_thread.start()


    def Stop(self):
        self.new_thread = thread.ControlThread(self.setdevice)
        self.new_thread.operation_num = 2
        self.new_thread.start()

    def ScanStop(self):
        self.new_thread.laser_stage.flag = 0


    
    def EmumDevice(self):
        pymotor.enum_device()
        print('\nemum complete!\n')
        self.device_name ,self.dev_count = pymotor.enum_device()
        self.device = numpy.empty(5,dtype=object)
        if self.dev_count == 0:
            print("\nNo finding of device.")
            print("\nUse the vitual device:\n")
            self.device_name = ["testxmotor","testymotor","testzmotor"]
            self.i = 0
            for self.str_device in self.device_name:
                print('str_device:'+self.str_device)
                self.device[self.i] = vitual_dev.VitualDevice(self.device_name[self.i])
                print('device[]' + str(self.device[self.i]))
                #self.testmotor = pymotor.Motor(vitual_dev.VitualDevice(self.str_device).open_name)
                #self.testmotor.move(10)
                self.i = self.i + 1
        else:
            for self.dev_ind in range(0,self.dev_count):
                self.device[self.dev_ind] =pymotor.Motor(self.device_name[self.dev_ind])
        
            
        
    
    def CurrentPosition(self):
        if tctEnable:
            self.currentPosX = self.setdevice[0].get_status_position()
            self.currentPosY = self.setdevice[1].get_status_position()
            self.currentPosZ = self.setdevice[2].get_status_position()

    def UpdateDesiredPos(self):
        if tctEnable:
            self.CurrentPosition()
            self.ui.CurrentPosX.display(self.currentPosX)
            self.ui.CurrentPosX_2.display(self.currentPosX)
            self.ui.CurrentPosY.display(self.currentPosY)
            self.ui.CurrentPosY_2.display(self.currentPosY)
            self.ui.CurrentPosZ.display(self.currentPosZ)
            self.ui.CurrentPosZ_2.display(self.currentPosZ)
            self.timer.start(500)
    def SetFolder(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        dlg.setFilter(QtCore.QDir.Files)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            print(repr(filenames))
            self.ui.FolderText.setText(filenames[0])



    def SaveData(self):
        self.capture_thread = thread.DataCapture()
        self.capture_thread.flag = True
        self.capture_thread.resource = self.ui.Interface.currentText()
        self.capture_thread.folder = self.ui.FolderText.text()
        self.capture_thread.device = self.setdevice
        self.capture_thread.frequency = self.ui.Frequency.value()
        self.capture_thread.point_num = self.ui.Points.value()
        self.capture_thread.ymult = float(self.ui.ymult.text())
        self.capture_thread.yzero = float(self.ui.yzero.text())
        self.capture_thread.yoff = float(self.ui.yoff.text())
        self.capture_thread.xincr = float(self.ui.xincr.text())
        self.capture_thread.xzero = float(self.ui.xzero.text())
        self.capture_thread.start()

    def CapturePause(self):
        self.capture_thread.flag = False



    def Ready(self):
        self.readythread = thread.ReadyThread()
        self.readythread.resource_name = self.ui.Interface.currentText()
        self.readythread.channel = self.ui.Channel.value()
        self.readythread.point_number = self.ui.Points.value()
        self.readythread.start()
        self.readythread.sinOut.connect(lambda:self.DisplayReadyInfo(self.readythread.message))

    def DisplayReadyInfo(self,dis_message):
        if dis_message == 'offset':
            self.ui.InfoText.append("read offset complete!")
            self.ui.ymult.setText(str(self.readythread.ymult))
            self.ui.yzero.setText(str(self.readythread.yzero))
            self.ui.yoff.setText(str(self.readythread.yoff))
            self.ui.xincr.setText(str(self.readythread.xincr))
            self.ui.xzero.setText(str(self.readythread.xzero))
        else:
            self.ui.InfoText.append(dis_message)







if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWidget()

    sys.exit(app.exec_())
