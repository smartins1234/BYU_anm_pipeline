import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
import pipe.pipeHandlers.pipeline_io as pio

class ToolCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        tool_list = self.project.list_tools()

        self.item_gui = sfl.SelectFromList(
            l=tool_list, parent=hou.ui.mainQtWindow(), title="Select a tool to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        name = value[0]

        body = self.project.get_tool(name)
        element = body.get_element(Asset.HDA)

        if element.get_last_version() < 0:
            qd.error("Nothing has been published for this tool")
            return
        filepath = element.get_last_publish()[3]

        hou.hda.installFile(filepath)
        stage = hou.node("/stage")

        try:
            hda = stage.createNode(name)
        except:
            qd.error("Couldn't create node of type " + name + ". You should still be able to tab in the node manually.")
            return

        try:
            hda.setName(name, 1)
        except:
            pass

        try:
            hda.allowEditOfContents()
        except:
            pass

        