"""
ChromaticAberrationWidget.py
Adds a widget and functionality for applying chromatic aberration
to an image. A few properties can be configured.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QDial, QSlider, QCheckBox, QVBoxLayout
from ctypes import *
from threading import Thread
from . import LibHandler

# Structures for C functions
class Coords(Structure):
    _fields_ = [("x", c_longlong),
                ("y", c_longlong)]

class RadialFilterData(Structure):
    _fields_ = [("power", c_int),
                ("deadzone", c_int),
                ("expFalloff", c_char),
                ("biFilter", c_char)]

class LinearFilterData(Structure):
    _fields_ = [("power", c_int),
                ("direction", c_int),
                ("biFilter", c_char)]

# Widget for chromatic aberration effect
class ChromAbWidget(QWidget):
    def __init__(self, parent=None):
        super(ChromAbWidget, self).__init__(parent)

        self.maxD = 20
        self.deadZ = 5
        self.isShapeRadial = True
        self.isFalloffExp = True
        self.direction = 100
        self.interpolate = False
        self.numThreads = 4

        self.shapeInfo = QLabel("Shape and Direction:", self)
        self.shapeChoice = QButtonGroup(self)
        self.shapeBtn1 = QRadioButton("Radial")
        self.shapeBtn2 = QRadioButton("Linear")
        self.shapeChoice.addButton(self.shapeBtn1)
        self.shapeChoice.addButton(self.shapeBtn2)
        self.shapeBtn1.setChecked(True)
        self.shapeBtn1.pressed.connect(self.changeShape1)
        self.shapeBtn2.pressed.connect(self.changeShape2)

        self.theDial = QDial()
        self.theDial.setMinimum(0)
        self.theDial.setMaximum(359)
        self.theDial.setValue(100)
        self.theDial.setWrapping(True)
        self.theDial.valueChanged.connect(self.updateDial)

        self.maxInfo = QLabel("Max Displacement: 20px", self)
        self.maxDisplace = QSlider(Qt.Horizontal, self)
        self.maxDisplace.setRange(1, 300)
        self.maxDisplace.setValue(20)
        self.maxDisplace.valueChanged.connect(self.updateMax)

        self.falloffInfo = QLabel("Falloff:", self)
        self.falloffChoice = QButtonGroup(self)
        self.foBtn1 = QRadioButton("Exponential")
        self.foBtn2 = QRadioButton("Linear")
        self.falloffChoice.addButton(self.foBtn1)
        self.falloffChoice.addButton(self.foBtn2)
        self.foBtn1.setChecked(True)
        self.foBtn1.pressed.connect(self.changeFalloff1)
        self.foBtn2.pressed.connect(self.changeFalloff2)

        self.deadInfo = QLabel("Deadzone: 5%", self)
        self.deadzone = QSlider(Qt.Horizontal, self)
        self.deadzone.setRange(0, 100)
        self.deadzone.setValue(5)
        self.deadzone.valueChanged.connect(self.updateDead)
        
        self.biFilter = QCheckBox("Bilinear Interpolation (slow, but smooths colors)", self)
        self.biFilter.stateChanged.connect(self.updateInterp)

        self.threadInfo = QLabel("Number of Worker Threads (FOR ADVANCED USERS): 4", self)
        self.workThreads = QSlider(Qt.Horizontal, self)
        self.workThreads.setRange(1, 64)
        self.workThreads.setValue(4)
        self.workThreads.valueChanged.connect(self.updateThread)

        vbox = QVBoxLayout()
        vbox.addWidget(self.shapeInfo)
        vbox.addWidget(self.shapeBtn1)
        vbox.addWidget(self.shapeBtn2)
        vbox.addWidget(self.theDial)
        vbox.addWidget(self.maxInfo)
        vbox.addWidget(self.maxDisplace)
        vbox.addWidget(self.falloffInfo)
        vbox.addWidget(self.foBtn1)
        vbox.addWidget(self.foBtn2)
        vbox.addWidget(self.deadInfo)
        vbox.addWidget(self.deadzone)
        vbox.addWidget(self.biFilter)
        vbox.addWidget(self.threadInfo)
        vbox.addWidget(self.workThreads)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateMax(self, value):
        self.maxInfo.setText("Max Displacement: " + str(value) + "px")
        self.maxD = value

    def updateDead(self, value):
        self.deadInfo.setText("Deadzone: " + str(value) + "%")
        self.deadZ = value

    def changeShape1(self):
        self.isShapeRadial = True

    def changeShape2(self):
        self.isShapeRadial = False

    def changeFalloff1(self):
        self.isFalloffExp = True

    def changeFalloff2(self):
        self.isFalloffExp = False

    def updateDial(self, value):
        self.direction = value

    def updateInterp(self, state):
        if state == Qt.Checked:
            self.interpolate = True
        else:
            self.interpolate = False

    def updateThread(self, value):
        self.threadInfo.setText("Number of Worker Threads (FOR ADVANCED USERS): " + str(value))
        self.numThreads = value

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize):
        newData = create_string_buffer(imgSize[0] * imgSize[1] * 4)
        
        dll = LibHandler.GetSharedLibrary()
        dll.ApplyLinearAberration.argtypes = [c_longlong, c_longlong, LinearFilterData, Coords, c_void_p, c_void_p]
        dll.ApplyRadialAberration.argtypes = [c_longlong, c_longlong, RadialFilterData, Coords, c_void_p, c_void_p]
        
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        threadPool = []
        interp = 0
        if self.interpolate:
                interp = 1
        if self.isShapeRadial:
            falloff = 0
            if self.isFalloffExp:
                falloff = 1
            filterSettings = RadialFilterData(self.maxD, self.deadZ, falloff, interp)
        else:
            filterSettings = LinearFilterData(self.maxD, self.direction, interp)
        idx = 0
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            if self.isShapeRadial:
                workerThread = Thread(target=dll.ApplyRadialAberration, args=(idx, numPixels, filterSettings,
                                        imgCoords, cimgData.from_buffer(imgData), byref(newData),))
            else:
                workerThread = Thread(target=dll.ApplyLinearAberration, args=(idx, numPixels, filterSettings,
                                        imgCoords, cimgData.from_buffer(imgData), byref(newData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        # Join threads to finish
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)