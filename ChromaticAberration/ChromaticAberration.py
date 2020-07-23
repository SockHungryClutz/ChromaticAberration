from krita import *
from . import UIController

class ChromaticAberration(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def FilterMainWindow(self):
        self.uiController = UIController.UIController()
        self.uiController.initialize()

    def createActions(self, window):
        action = window.createAction("OpenCAFilter", "Chromatic Aberration")
        action.triggered.connect(self.FilterMainWindow)

Krita.instance().addExtension(ChromaticAberration(Krita.instance()))
