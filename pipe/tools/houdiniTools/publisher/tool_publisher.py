import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

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


    '''def publish(self):
        tool_list = self.project.list_tools()
        tool_list.append("New Tool")

        self.item_gui = sfl.SelectFromList(
            l=tool_list, parent=hou.ui.mainQtWindow(), title="Select a tool to publish")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        name = value[0]
        self.toolName = name

        if name == "New Tool":
            self.create_tool()
            return
        
        tool = self.project.get_tool(name)
        if not tool:
            qd.error("This tool doesn't seem to exist. If you know it does, get Stephanie to come fix it :P")
        
        self.element = tool.get_element(Asset.HDA)

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
        self.filepath = os.path.join(self.element._filepath, name + "_main.hda")
        definition.save(self.filepath, hda)

        publishes = self.element.list_publishes()
        publishes_string_list = ""
        for publish in publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label
        
        self.input = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment ", info=publishes_string_list)
        self.input.submitted.connect(self.comment_results)

    def create_tool(self):
        self.input = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Enter the tool's name ")
        self.input.submitted.connect(self.name_results)

    def name_results(self, value):
        #name = str(value)
        #name = name.replace(" ", "")
        

        self.toolName = name

        tool = self.project.create_tool(name)
        if not tool:
            qd.error("Unable to create tool.")
            return
        self.element = tool.get_element(Asset.HDA)

        selection = hou.selectedNodes()
        if len(selection) != 1:
            qd.error(
                'Please select a single Digital Asset node to publish.')
            return
        if not selection[0].type().definition():
            qd.error(
                'Please select Digital Asset node to publish.')
            return

        hda = selection[0]
        definition = hda.type().definition()
        self.filepath = os.path.join(self.element._filepath, name + "_main.hda")
        definition.save(self.filepath, hda)
        hda = None
        self.filepath = os.path.join(self.element._filepath, name + "_main.hda")
        hda = selection[0].createDigitalAsset(name=name, hda_file_name=self.filepath, ignore_external_references=True)
        definition = hda.type().definition()
        definition.save(self.filepath)

        self.input = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment ")
        self.input.submitted.connect(self.comment_results)'''

    def comment_results(self, value):
        comment = str(value)
        username = Environment().get_user().get_username()

        self.element.update_app_ext(".hda")
        self.element.publish(username, self.filepath, comment, self.name)