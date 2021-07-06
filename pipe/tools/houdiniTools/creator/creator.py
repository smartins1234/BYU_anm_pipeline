import os, hou

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers import pipeline_io
from pipe.tools.houdiniTools.assembler.assembler import Assembler
from PySide2 import QtWidgets


class Creator:

    def __init__(self):
        self.name = None
        self.type = None

    def run(self, type=None):
        self.type = type
        self.create_body()

    '''
    This will bring up the create new body UI
    '''
    def create_body(self):
        titlestring = "What is the name of this " + self.type + "?"
        self.input = qd.HoudiniInput(parent=hou.qt.mainWindow(), title=titlestring)
        self.input.submitted.connect(self.name_results)

    def name_results(self, value):
        self.name = str(value)

        name = str(self.name)
        if not pipeline_io.checkFileName(name):
            self.create_body()
            return

        if self.name is None or self.name == "":
            return

        asset_type_list = AssetType().list_asset_types()

        if self.type:
            self.results([self.type])
            return

        self.item_gui = sfl.SelectFromList(l=asset_type_list, parent=hou.qt.mainWindow(), title="What are you creating?", width=250, height=160)
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        type = value[0]
        name = self.name

        # determine if asset was created or not.
        created = True

        if name is None or type is None:
            created = False

        if created:
            project = Project()
            body = project.create_asset(name, asset_type=type)
            selectedNodes = []

            for node in hou.selectedNodes():
                if node.type().category() == hou.sopNodeTypeCategory():
                    selectedNodes.append(node)
                elif node.type().category() == hou.objNodeTypeCategory():
                    if selectedNodes:
                        qd.error("Selected nodes for asset must be inside a geo node or a single geo node.")
                    selectedNodes = node.children()
                    break

            if body == None:
                qd.error("Asset with name " + name + " already exists in pipeline.")
            elif self.type == AssetType.SHOT:
                qd.info("Shot created successfully.", "Success")
            else:
                assembler = Assembler()
                HDA = assembler.create_hda(name, body=body, selected_nodes=selectedNodes)
                HDA.updateFromNode(HDA)
                qd.info("Asset created successfully.", "Success")

        else:
            qd.error("Asset creation failed.")
