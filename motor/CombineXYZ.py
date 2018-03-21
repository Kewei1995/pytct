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
    import VitualDevice as vitual_dev

testpass = False


class Axis(QtWidgets.QWidget):
    def __init__(self, parent, Title, Device, uiFile):
        super(Axis, self).__init__(parent)

        self.ui = uic.loadUi(uiFile)
        self.timer = QtCore.QTimer()
        self.Device = Device
        #Declaring Device
        if tctEnable:
            self.SetMotor()
            
            

        #Move
        self.ui.MoveButton.clicked.connect(lambda:self.MoveAB(int(self.ui.SetPosX.text()), int(self.ui.SetPosY.text()), int(self.ui.SetPosZ.text())))

        #Step move X
        self.ui.XPlus.clicked.connect(lambda:self.MoveRE(self.Xaxis,self.ui.StepMoveX.value()))
        self.ui.XMinus.clicked.connect(lambda:self.MoveRE(self.Xaxis,-self.ui.StepMoveX.value()))

        #Step move Y
        self.ui.YPlus.clicked.connect(lambda:self.MoveRE(self.Yaxis,self.ui.StepMoveY.value()))
        self.ui.YMinus.clicked.connect(lambda:self.MoveRE(self.Yaxis,-self.ui.StepMoveY.value()))

        #Step move Z
        self.ui.ZPlus.clicked.connect(lambda:self.MoveRE(self.Zaxis,self.ui.StepMoveZ.value()))
        self.ui.ZMinus.clicked.connect(lambda:self.MoveRE(self.Zaxis,-self.ui.StepMoveZ.value()))

        #Home
        self.ui.ResetPosX.clicked.connect(lambda:self.Home(self.Xaxis))
        self.ui.ResetPosY.clicked.connect(lambda:self.Home(self.Yaxis))
        self.ui.ResetPosZ.clicked.connect(lambda:self.Home(self.Zaxis))

        #scan
        self.ui.ScanBut.clicked.connect(lambda:self.Scan(self.Xaxis,self.Yaxis,self.Zaxis))

        #set motor
        self.ui.SetMotor.clicked.connect(self.SetMotor)

         # Var
        self.currentPosX = 0
        self.currentPosY = 0
        self.currentPosZ = 0
        self.Title = Title

        #####################
        # Initializing Widget
        self.UpdateDesiredPos()
        self.ui.setWindowTitle(Title)

       
        #self.lenght = self.ui.DesirePos.maximum()

    def Home(self,motor):
        ret = QtWidgets.QMessageBox.warning(self, "Homming",
                "Please Check the setup!\n\nAre you sure you really want\nto Home the motor?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Escape)
        if ret == QtWidgets.QMessageBox.Yes:
            if tctEnable:
                motor.home()
            else:
                self.ui.StatusLabel.setText("Home")
        self.UpdateDesiredPos()

    def Stop(self):
        if tctEnable:
            self.Xaxis.stop()
        else:
            self.ui.StatusLabel.setText("")

        self.UpdateDesiredPos()
    '''
    def Limits(self):
        self.Limits = Limits(self)
    '''
    def MoveAB(self,pos_X,pos_Y,pos_Z):
        if tctEnable:
            self.Xaxis.move(pos_X)
            self.Yaxis.move(pos_Y)
            self.Zaxis.move(pos_Z)
        self.UpdateDesiredPos()

    def MoveRE(self,motor,movement):
        UpperLimit = 100 #self.ui.DesirePos.maximum()
        LowerLimit = -100    #self.ui.DesirePos.minimum()
        currentPos = motor.get_status_position()
        if currentPos + movement > UpperLimit:
            movement = UpperLimit - currentPos
        elif currentPos + movement < LowerLimit:
            movement = LowerLimit - currentPos

        if tctEnable:
            motor.forward(movement)
        time.sleep(0.1)
        self.UpdateDesiredPos()

    def Scan(self,motor1,motor2,motor3):
        self.x0 = self.ui.x0.value() 
        self.y0 = self.ui.y0.value()
        self.z0 = self.ui.z0.value()
        self.dx = self.ui.dx.value()
        self.dy = self.ui.dy.value()
        self.dz = self.ui.dz.value()
        self.Nx = self.ui.Nx.value()
        self.Ny = self.ui.Ny.value()
        self.Nz = self.ui.Nz.value()
        
        self.MoveAB(self.x0,self.y0,self.z0)
        #delay 1 second for motor moving to (x0,y0.z0)
        time.sleep(2)
    
        # # scan step by step
        # self.flag1 = self.flag2 = -1
        # for self.i in range(0, self.Nz):
        #     self.MoveRE(self.Zaxis, self.dz)
        #     self.flag1 = self.flag1 * (-1)
        #     for self.j in range(0, self.Nx):
        #         self.MoveRE(self.Xaxis, self.flag1 * self.dx)
        #         self.flag2 = self.flag2 * (-1)
        #         for self.k in range(0, self.Ny):
        #             self.MoveRE(self.Yaxis, self.flag2 * self.dy)
        #             #print(self.Xaxis.get_status_position(),self.Yaxis.get_status_position(),self.Zaxis.get_status_position())
        #             print(self.ui.CurrentPosX_2.value(),self.ui.CurrentPosY_2.value(),self.ui.CurrentPosZ_2.value())
        #             self.timer.timeout.connect(self.UpdateDesiredPos)
        #             self.timer.start(100)
        #             #self.UpdateDesiredPos() 
                    





    
        for self.PZ in range(self.z0, self.z0 + ((self.Nz + 1) * self.dz) , self.dz):
            for self.PX in range(self.x0, self.x0 + ((self.Nx + 1) * self.dx) , self.dx):
                for self.PY in range(self.y0, self.y0 + ((self.Ny + 1) * self.dy) , self.dy):
                    self.MoveAB(self.PX, self.PY, self.PZ)
                    print(self.Xaxis.get_status_position(),self.Yaxis.get_status_position(),self.Zaxis.get_status_position())
                    self.timer.timeout.connect(self.UpdateDesiredPos)
                    self.timer.start(100)
                    #time.sleep(0.1)

    def SetMotor(self):
        self.Xaxis = self.Device[self.ui.X_Motor_Num.value()-1]
        self.Yaxis = self.Device[self.ui.Y_Motor_Num.value()-1]
        self.Zaxis = self.Device[self.ui.Z_Motor_Num.value()-1]
            
        
    
    def CurrentPosition(self):
        if tctEnable:
            self.currentPosX = self.Xaxis.get_status_position()
            self.currentPosY = self.Yaxis.get_status_position()
            self.currentPosZ = self.Zaxis.get_status_position()
    def UpdateDesiredPos(self):
        if tctEnable:
            self.CurrentPosition()
            self.ui.CurrentPosX.display(self.currentPosX)
            self.ui.CurrentPosX_2.display(self.currentPosX)
            self.ui.CurrentPosY.display(self.currentPosY)
            self.ui.CurrentPosY_2.display(self.currentPosY)
            self.ui.CurrentPosZ.display(self.currentPosZ)
            self.ui.CurrentPosZ_2.display(self.currentPosZ)
            self.timer.start(100)

    def run(self):
        self.ui.show()

class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        self.stack = QtWidgets.QStackedWidget()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)

        ################################################
        #initialize the device information,search usable device
        pymotor.enum_device()
        print('\nemum complete!\n')
        self.devenum ,self.dev_count = pymotor.enum_device()
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
                self.device[self.dev_count] =pymotor.Motor(pymotor.Motor.get_name(self,self.devenum,self.dev_ind))



        ##############################################################

        XYZD_Title = "XYZ Motor"
        XYZD_uiFile = "GUI/XYZWidget.ui"
        self.XYZDetector = Axis(self, XYZD_Title, self.device, XYZD_uiFile)

        self.stack.addWidget(self.XYZDetector)

        self.XYZDetector.run()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWidget()

    sys.exit(app.exec_())
