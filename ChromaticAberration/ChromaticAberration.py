from krita import *
from PyQt5.QtCore import QSettings, QStandardPaths
from . import UIController

class ChromaticAberration(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def FilterMainWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController.UIController()
        self.uiController.initialize(self)

    def createActions(self, window):
        action = window.createAction("OpenCAFilter", "Chromatic Aberration")
        action.triggered.connect(self.FilterMainWindow)

Krita.instance().addExtension(ChromaticAberration(Krita.instance()))
