from PySide2 import QtWidgets, QtGui, QtCore
from pipe.pipeHandlers.project import Project
import os

class SelectFromList(QtWidgets.QDialog):

    submitted = QtCore.Signal(list)

    def __init__(self, parent=None, title="Select", l=[], multiple_selection=False, width=600, height=600):
        super(SelectFromList, self).__init__(parent)
        if parent:
            self.parent = parent
        print(self.parent)
        self.show()
        print("where's my window?")