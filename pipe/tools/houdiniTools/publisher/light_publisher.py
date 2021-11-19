import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Shot, Asset, Sequence
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment

class LightPublisher:
    def __init__(self):
        self.project = Project()

    def publish(self):
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(
            l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to publish to")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        self.shot_name = value[0]

        shot = self.project.get_shot(self.shot_name)
        if not shot:
            shot = self.project.create_shot(self.shot_name)
        if not shot:
            qd.error("Get Stephanie, because something broke bad.")
        self.element = shot.get_element(Asset.LIGHTS)

        if len(hou.selectedNodes()) != 1:
            qd.error("Only select the last node in the network of lights.")
            return

        last = hou.selectedNodes()[0]
        rop = hou.node("/stage").createNode("usd_rop")
        rop.setInput(0, last)

        self.savePath = os.path.join(self.element._filepath, "temp.usda")
        rop.parm("lopoutput").set(self.savePath)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)

        rop.parm("execute").pressButton()

        rop.destroy()

        publishes = self.element.list_publishes()
        publishes_string_list = ""
        for publish in publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label
        
        self.comment = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment for publish?", info=publishes_string_list)
        self.comment.submitted.connect(self.comment_results)

    def comment_results(self, value):
        comment = str(value)
        username = Environment().get_user().get_username()
        self.element.update_app_ext(".usda")
        self.element.publish(username, self.savePath, comment, self.shot_name)