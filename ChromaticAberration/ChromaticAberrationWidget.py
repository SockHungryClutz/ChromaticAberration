"""
ChromaticAberrationWidget.py
Adds a widget and functionality for applying chromatic aberration
to an image. The max displacement and deadzone can be configured.
All other options are locked for now, as this is based on physical
cameras as far as I know.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QDial, QSlider, QCheckBox, QVBoxLayout
import math

# Helper functions for vector math and color sampling
# Get color data as a list(4) based on the index
def getColorAtIndex(idx, imgData):
    idx2 = idx*4
    # convert to int before returning, simplifies math and conversions
    return [byte2Int(imgData[idx2]), byte2Int(imgData[idx2+1]), byte2Int(imgData[idx2+2]), byte2Int(imgData[idx2+3])]

def byte2Int(byt):
    return int.from_bytes(byt, byteorder='little', signed=False)

# numpy isn't really an option if I want to share this
def scaleVect(vect, scalar):
    return [i * scalar for i in vect]

def addVect(vect1, vect2):
    return [vect1[i] + vect2[i] for i in range(len(vect1))]

def lenVect(vect):
    return math.sqrt((vect[0] ** 2) + (vect[1] ** 2))

# Get a color sample at some coordinate, works with float coords using bilinear
# Or skip bilinear interpolation for speedup
def sampleAt(coords, interp, imgData, imgSize):
    # clamp to image bounds
    x = max(0.0, min(coords[0], imgSize[0]-1))
    y = max(0.0, min(coords[1], imgSize[1]-1))
    # get offset from exact pixel
    rx = x % 1
    ry = y % 1
    x = math.floor(x)
    y = math.floor(y)

    baseColor = getColorAtIndex((y * imgSize[0]) + x, imgData)
    if interp:
        # blend colors between 4 pixels to get the final result (bilinear)
        if ry > 0.00001:
            baseColor = addVect(scaleVect(baseColor, 1.0-ry), scaleVect(getColorAtIndex(((y+1)*imgSize[0])+x, imgData), ry))
        if rx > 0.00001:
            color2 = getColorAtIndex((y * imgSize[0]) + x + 1, imgData)
            if ry > 0.00001:
                color2 = addVect(scaleVect(color2, (1.0-ry)), scaleVect(getColorAtIndex(((y+1)*imgSize[0])+x+1, imgData), ry))
            baseColor = addVect(scaleVect(baseColor, (1-rx)), scaleVect(color2, rx))
    return baseColor

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

    # Return the new color of the pixel at the specified index
    def applyOnePixel(self, coords, imgData, imgSize):
        baseColor = getColorAtIndex((coords[1] * imgSize[0]) + coords[0], imgData)
        # linear direction is easy
        if not self.isShapeRadial:
            displace = [-1*math.sin(math.radians(self.direction)), math.cos(math.radians(self.direction))]
            displace = scaleVect(displace, self.maxD)
        else:
            # get direction vector
            floatDeadzone = self.deadZ / 100
            center = ((imgSize[0]-1)/2, (imgSize[1]-1)/2)
            displace = addVect(coords, scaleVect(center, -1))
            # normalize, length of displace will be [0,1]
            displace = scaleVect(displace, 1/lenVect(center))
            # if inside the deadzone, return original color
            if lenVect(displace) <= floatDeadzone:
                return baseColor
            else:
                # scale vector to 0 at the edge of deadzone, 1 at edge of screen
                displace = scaleVect(displace, (lenVect(displace) - floatDeadzone) * (1/(1-floatDeadzone)))
                # use exponential falloff
                if self.isFalloffExp:
                    displace = scaleVect(displace, lenVect(displace))
                # scale vector to final length based on max displacement
                displace = scaleVect(displace, self.maxD)
                # return immediately if vector is insignificant
                if lenVect(displace) < 0.01:
                    return baseColor
        # blend original green channel with blue and red from other pixels
        redChannel = sampleAt(addVect(coords, displace), self.interpolate, imgData, imgSize)
        blueChannel = sampleAt(addVect(coords, scaleVect(displace, -1)), self.interpolate, imgData, imgSize)
        # blend transparency
        transparent = (redChannel[3] / 3) + (blueChannel[3] / 3) + (baseColor[3] / 3)
        return [redChannel[0], baseColor[1], blueChannel[2], transparent]

    # Iterate over the image applying the filter
    def applyFilter(self, imgData, imgSize):
        # preallocate to save time
        newData = [0] * (imgSize[0] * imgSize[1])
        idx = 0
        while idx < imgData.length():
            # convert to x,y coordinates
            coords = ((idx/4) % imgSize[0], (idx/4) // imgSize[0])
            newPixel = self.applyOnePixel(coords, imgData, imgSize)
            for i in range(4):
                # truncate to int
                newData[idx + i] = int(newPixel[i])
            idx += 4
        return bytes(newData)