from PySide2 import QtWidgets, QtCore, QtGui
import os #, hou        we can't have import hou here because it makes it break on the maya side
from pipe.pipeHandlers.project import Project

'''Reports a critical error'''


def error(errMsg, details=None, title='Error'):
    message(errMsg, details=details, title=title)

    '''Reports a non-critical warning'''


def warning(warnMsg, details=None, title='Warning'):
    message(warnMsg, details=details, title=title)

    '''Reports a message'''


def message(msg=' ', details=None, title='Message'):
    print(msg)

    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(msgBox.tr(msg))
    if title == 'Warning':
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    elif title == 'Error':
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    else:
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
    msgBox.setWindowTitle(title)
    msgBox.addButton(QtWidgets.QMessageBox.Ok)

    if details is not None:
        msgBox.setDetailedText(str(details))

    msgBox.exec_()

    '''Reports an informational message'''


def info(infoMsg, title='Info'):
    message(msg=infoMsg, title=title)


def light_error(errMsg, title='Warning'):
    '''Reports an error that can be resolved with a yes or no'''
    '''returns True if yes, otherwise False'''
    return yes_or_no(errMsg, title=title)


def yes_or_no(question, details=None, title='Question'):
    '''Asks a question that can be resolved with a yes or no'''
    '''returns True if yes, otherwise False'''
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(msgBox.tr(question))
    msgBox.setWindowTitle(title)
    if title == 'Question':
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
    else:
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
    yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

    if details is not None:
        msgBox.setDetailedText(details)

    msgBox.exec_()

    if msgBox.clickedButton() == yesButton:
        return True
    elif msgBox.clickedButton() == noButton:
        return False


def input(label, title='Input', text=None):
    '''
    Allows the user to respond with a text input
    If the okay button is pressed it returns the inputed text, otherwise None
    '''
    dialog = QtWidgets.QInputDialog()
    text = dialog.getText(None, title, label, text=text)

    if text[1]:
        return text[0]
    else:
        return None


'''
	Have to use this instead of input in houdini to avoid black text on black bar
'''


class HoudiniInput(QtWidgets.QDialog):
    '''
    submitted is a class variable that must be instantiated outside of __init__
    in order for the Signal to be created correctly.
    '''
    submitted = QtCore.Signal(list)

    def __init__(self, parent=None, title="Enter info", width=350, height=75):
        super(HoudiniInput, self).__init__(parent)

        if parent:
            self.parent = parent
        self.setWindowTitle(title)
        self.setObjectName('HoudiniInput')
        self.resize(width, height)
        self.initializeVBox()
        self.setLayout(self.vbox)
        self.show()

    def initializeVBox(self):
        self.vbox = QtWidgets.QVBoxLayout()
        #QApplication.setActiveWindow()
        self.initializeTextBar()
        self.initializeSubmitButton()

    def initializeTextBar(self):
        hbox = QtWidgets.QHBoxLayout()
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setStyleSheet(
            "color: white; selection-color: black; selection-background-color: white;")
        self.text_input.textEdited.connect(self.textEdited)
        self.text_input.setFocus()
        hbox.addWidget(self.text_input)
        self.vbox.addLayout(hbox)

    def initializeSubmitButton(self):
        # Create the button widget
        self.button = QtWidgets.QPushButton("Confirm")
        self.button.setDefault(True)
        self.button.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.button.clicked.connect(self.submit)
        self.button.setEnabled(False)
        self.vbox.addWidget(self.button)

    def textEdited(self, newText):
        if len(newText) > 0:
            self.button.setEnabled(True)
            self.button.setDefault(True)
        else:
            self.button.setEnabled(False)

        self.values = newText

    '''Get the current state of the loading indicator gif as an icon'''

    def setButtonIcon(self, frame):
        icon = QtGui.QIcon(self.movie.currentPixmap())
        self.button.setIcon(icon)

    '''
    	Send the selected values to a function set up in the calling class and
    	close the window. Use connect() on submitted to set up the receiving func.
    '''

    def submit(self):
        print('comment input: '+ self.values +'\n')
        self.button.setText("Loading...")
        icon_path = os.path.join(Project().get_project_dir(
        ), "pipe", "tools", "_resources", "loading_indicator_transparent.gif")
        self.movie = QtGui.QMovie(icon_path)
        self.movie.frameChanged.connect(self.setButtonIcon)
        if not self.movie.loopCount() == -1:
            self.movie.finished().connect(self.movie.start())
        self.movie.start()
        self.button.setEnabled(False)
        self.submitted.emit(self.values)
        self.close()



class VersionWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):#=hou.qt.mainWindow()):  # you're going to have to set the parent explicitly when you call this function
        super(VersionWindow, self).__init__(parent)     # because importing hou raises an error when this runs in maya

        # Function to build the UI
        # Create main widget
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)

        # Initialize the layout
        global_layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QFormLayout()
        main_widget.setLayout(global_layout)

        # Create Controls - Display Current Version
        self.current_version_label = QtWidgets.QLabel()
        self.current_version_label.setMinimumWidth(300)
        # Create Controls - Display Library Path
        self.current_path_label = QtWidgets.QLabel()
        # Create Controls - Display Divider
        line = QtWidgets.QFrame()
        line.setFrameStyle(QtWidgets.QFrame.HLine |
                           QtWidgets.QFrame.Sunken)
        # Create Controls - Major version int editor
        self.major_version = QtWidgets.QSpinBox()
        # Create Controls - Minor version int editor
        self.minor_version = QtWidgets.QSpinBox()
        # Create Controls - custom spin box that supports a zero padded syntax for integers (001 instead of 1)
        self.revision_version = PaddedSpinBox()
        # Create Controls - Create New Version button
        self.set_version = QtWidgets.QPushButton(
            'Create New Version')

        # Add controls to layout and set label
        layout.addRow('Current Version:', self.current_version_label)
        layout.addRow('Library Path:', self.current_path_label)
        layout.addRow(line)
        layout.addRow('Major Version:', self.major_version)
        layout.addRow('Minor Version:', self.minor_version)
        layout.addRow('Revision Version:', self.revision_version)

        # Global layout setting
        global_layout.addLayout(layout)
        global_layout.addWidget(self.set_version)




# PySide2 UI - custom QSpinBox that supports a zero padded syntax
# Subclass PySide2.QtWidgets.QSpinBox
class PaddedSpinBox(QtWidgets.QSpinBox):
    def __init__(self, parent=None):
        super(PaddedSpinBox, self).__init__(parent)

    # Custom format of the actual value returned from the text
    def valueFromText(self, text):
        regExp = QtCore.QRegExp(("(\\d+)(\\s*[xx]\\s*\\d+)?"))

        if regExp.exactMatch(text):
            return regExp.cap(1).toInt()
        else:
            return 0

    # Custom format of the text displayed from the value
    def textFromValue(self, value):
        return str(value).zfill(3)


def large_input(label, title='Input', text=None):
    '''
    Allows the user to respond with a larger text input
    If the okay button is pressed it returns the inputed text, otherwise None
    '''

    dialog = QtWidgets.QTextEdit()
    # dialog.setCancelButtonText("Skip")toPlainText
    text = dialog.toPlainText(None, title, label, text=text)

    if text[1]:
        return text[0]
    else:
        return None


def binary_option(text, optionOne, optionTwo, title='Question'):
    '''Gives the user a message and a binary choice'''
    '''returns True if option one is selected, false if the second option is selected, otherwise None'''
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(msgBox.tr(text))
    msgBox.setIcon(QtWidgets.QMessageBox.Question)
    msgBox.setWindowTitle(title)
    fristButton = msgBox.addButton(
        msgBox.tr(optionOne), QtWidgets.QMessageBox.ActionRole)
    secondButton = msgBox.addButton(
        msgBox.tr(optionTwo), QtWidgets.QMessageBox.ActionRole)
    cancelButton = msgBox.addButton(QtWidgets.QMessageBox.Cancel)

    msgBox.exec_()

    if msgBox.clickedButton() == fristButton:
        return True
    elif msgBox.clickedButton() == secondButton:
        return False
    return None


def save(text):
    '''Prompts the user to save'''
    '''returns True if save is selected, False if don't save is selected otherwise None'''
    return binary_option(text, 'Save', 'Don\'t Save', title='Save Changes')
