import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset, Sequence
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

'''
publishes an hda as a sequence effect hda
'''
class FXPublisher:
    def __init__(self):
        self.project = Project()

    def go(self):
        sequence_list = self.project.list_sequences()

        self.item_gui = sfl.SelectFromList(
            l=sequence_list, parent=hou.ui.mainQtWindow(), title="Select a sequence to publish to")
        self.item_gui.submitted.connect(self.publish)


    def publish(self, value):
        self.name = value[0]
        self.sequence = self.project.get_sequence(self.name)
        if not self.sequence:
            self.sequence = self.project.create_sequence(self.name)
        if not self.sequence:
            qd.error("Bro, Stephanie really fumbled this one. No such sequence exists.")
            return

        selection = hou.selectedNodes()
        if len(selection) != 1:
            qd.error(
                'Please select a single Houdini Digital Asset node to publish.')
            return
        if not selection[0].type().definition():
            qd.error(
                'Please select a Houdini Digital Asset node to publish.')
            return

        hda = selection[0]
        self.definition = hda.type().definition()
        fxName = self.definition.nodeTypeName()

        dept = os.path.join(Asset.HDA, fxName)
        deptPath = os.path.join(self.sequence._filepath, dept)

        self.element = self.sequence.create_element(deptPath, Element.DEFAULT_NAME)
        if not self.element:
            self.element = self.sequence.get_element(dept)
        if not self.element:
            qd.error("Well that effect can't exist for some reason. Blame Stephanie.")


        self.definition.updateFromNode(hda)
        self.tempPath = os.path.join(self.element._filepath, "temp.hda")
        self.definition.save(self.tempPath)

        publishes = self.element.list_publishes()
        publishes_string_list = ""
        for publish in publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label
        
        self.input = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment ", info=publishes_string_list)
        self.input.submitted.connect(self.comment_results)


    def comment_results(self, value):
        comment = str(value)
        username = Environment().get_user().get_username()

        self.element.update_app_ext(".hda")
        self.element.publish(username, self.tempPath, comment, self.definition.nodeTypeName())