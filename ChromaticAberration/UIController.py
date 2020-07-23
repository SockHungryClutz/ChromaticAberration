"""
Class that controls the UI model for the plugin
"""
from krita import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout
from . import ChromaticAberrationWidget

# Simple dialog box for the filters
class MainDialog(QDialog):
    def __init__(self, uiController, parent=None):
        super(MainDialog, self).__init__(parent)
        self.uiController = uiController

    def closeEvent(self, event):
        pass

class UIController(object):
    def __init__(self):
        self.mainWidget = MainDialog(self)
        self.warningWidget = QLabel()
        self.doNotSave = False
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self.mainWidget)
        self.mainWidget.setWindowModality(Qt.WindowModal)

    def initialize(self):
        self.buttonBox.accepted.connect(self.applyChanges)
        self.buttonBox.rejected.connect(self.mainWidget.reject)

        vbox = QVBoxLayout(self.mainWidget)

        doc = Krita.instance().activeDocument()
        if not doc:
            self.warningWidget.setText("You need to have a document open to use this script!")
            vbox.addWidget(self.warningWidget)
            self.doNotSave = True
        elif doc.activeNode().colorModel() != "RGBA" or doc.activeNode().colorDepth() != "U8":
            self.warningWidget.setText("Color space for the layer must be set to 8bit RGBA!")
            vbox.addWidget(self.warningWidget)
            self.doNotSave = True
        else:
            self.filterWidget = ChromaticAberrationWidget.ChromAbWidget()
            vbox.addWidget(self.filterWidget)
            self.doNotSave = False
        vbox.addWidget(self.buttonBox)

        self.mainWidget.setWindowTitle("Chromatic Aberration")
        self.mainWidget.setGeometry(QRect(600, 200, 400, 200))
        self.mainWidget.setSizeGripEnabled(True)
        self.mainWidget.show()
        self.mainWidget.activateWindow()

    def applyChanges(self):
        if not self.doNotSave:
            doc = Krita.instance().activeDocument()
            curNode = doc.activeNode().duplicate()
            curNode.setName(curNode.name() + " - duplicate")
            resultData = self.filterWidget.applyFilter(curNode.projectionPixelData(0, 0, doc.width(), doc.height()), (doc.width(), doc.height()))
            curNode.setPixelData(resultData, 0, 0, doc.width(), doc.height())
            doc.rootNode().addChildNode(curNode, None)
            doc.refreshProjection()
        self.mainWidget.accept()