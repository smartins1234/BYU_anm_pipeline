import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

'''
publishes hdas to the pipeline
'''
class ToolPublisher:
    def __init__(self):
        self.project = Project()

    def publish(self):

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
        definition = hda.type().definition()
        self.name = definition.nodeTypeName()

        tool = self.project.get_tool(self.name)
        if not tool:
            tool = self.project.create_tool(self.name)
        self.element = tool.get_element(Asset.HDA)
        
        self.filepath = os.path.join(self.element._filepath, self.name)
        definition.save(self.filepath, hda)

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
        self.element.publish(username, self.filepath, comment, self.name)