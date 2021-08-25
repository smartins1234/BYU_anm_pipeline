import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

class ShotPublisher:
    def __init__(self):
        self.project = Project()

    def publish(self):
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(
            l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to publish")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        self.shot_name = value[0]

        shot = self.project.get_shot(self.shot_name)
        self.element = shot.get_element(Asset.HIP)

        self.path = os.path.join(self.element._filepath, "temp.hip")

        hou.hipFile.setName(self.shot_name)
        hou.hipFile.save(self.path, False)

        publishes = self.element.list_publishes()
        publishes_string_list = ""
        for publish in publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label

        self.input = qd.HoudiniInput(parent=hou.qt.mainWindow(), title="Comment ", info=publishes_string_list)
        self.input.submitted.connect(self.comment_results)

    def comment_results(self, value):
        comment = str(value)
        
        username = Environment().get_user().get_username()
        name = self.shot_name

        self.element.update_app_ext(".hip")
        self.element.publish(username, self.path, comment, name)