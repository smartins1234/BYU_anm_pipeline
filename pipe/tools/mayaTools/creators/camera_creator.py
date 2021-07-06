import os

from pipe.pipeHandlers.project import Project
from pipe.tools.mayaTools.utilities.utils import *
import pipe.pipeHandlers.select_from_list as sfl
import pipe.pipeHandlers.quick_dialogs as qd

class CameraCreator:

    def __init__(self):
        self.project = Project()

    def go(self):
        #get shot to add camera to
        shotList = self.project.list_existing_shots() #we shouldn't be adding cameras to shots that haven't been created yet anyway

        self.item_gui = sfl.SelectFromList(l=shotList, parent=maya_main_window(), title="Select shot to add extra camera to")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        shot_name = value[0]

        shot = self.project.get_shot(shot_name)
        if shot is None:
            qd.error("There was a problem loading the shot.")
            return

        prevNum = shot.get_camera_number()
        newNum = prevNum + 1
        shot.set_camera_number(newNum)

        message = "There are now " + str(newNum) + " cameras in shot " + shot_name

        qd.message(message)