import os

from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.project import Element
from pipe.pipeHandlers.project import Environment
from pipe.tools.mayaTools.utilities.utils import *

import maya.cmds as mc

class ShotSaver:
    def __init__(self):
        self.project = Project()
        qd.message("This action will save a copy of this Maya file in the groups folder, but will not publish " + 
            "anything to the pipeline.")

    def save(self):
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=maya_main_window(), title="Select a shot to save to")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        shot_name = value[0]
        self.item_gui.close()

        shot = self.project.get_shot(shot_name)
        element = None
        try:
            element = shot.get_element(Asset.MAYA)
        except:
            element = shot.create_element(Asset.MAYA, Element.DEFAULT_NAME)

        path = os.path.join(element._filepath, "temp.mb")
        mc.file(rename=path)
        mc.file(save=True, type="mayaBinary")

        self.publishes = element.list_publishes()
        publishes_string_list = ""
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label


        comment = qd.input(title="Comment on changes", label=publishes_string_list)
        username = Environment().get_user().get_username()

        element.update_app_ext(".mb")
        element.publish(username, path, comment, shot_name)