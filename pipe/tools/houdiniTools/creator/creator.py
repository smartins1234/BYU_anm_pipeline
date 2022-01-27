'''
This file is depricated, and only kept here as a reference.
'''

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
                HDA.type().definition().updateFromNode(HDA)
                #HDA.updateFromNode(HDA)
                qd.info("Asset created successfully.", "Success")

        else:
            qd.error("Asset creation failed.")

    def create_asset(self):
        project = Project()

        asset_list = project.list_existing_assets()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to create")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        asset_name = value[0]

        stage = hou.node("/stage")
        primpath = "/" + asset_name

        prim = stage.createNode("primitive")
        prim.setName("base_prim", 1)
        prim.parm("primpath").set(primpath)

        config = stage.createNode("configurelayer")
        config.setName("set_default_prim", 1)
        config.setInput(0, prim)
        config.parm("defaultprim").set(primpath)
        config.parm("setdefaultprim").set(1)

        ref1 = stage.createNode("reference")
        ref1.setName("blank_reference_1", 1)
        ref1.parm("primpath").set(primpath)
        lib1 = stage.createNode("materiallibrary")
        lib1.setInput(0, ref1)
        mat_asgn = stage.createNode("assignmaterial")
        mat_asgn.setInput(0, lib1)
        label = stage.createNode("null")
        label.setName(asset_name, 1)
        label.setInput(0, mat_asgn)

        graft = stage.createNode("graftstages")
        graft.parm("primpath").set(primpath)
        graft.parm("destpath").set("/")
        graft.setInput(0, config)
        graft.setInput(1, label)

        add_var = stage.createNode("addvariant")
        add_var.parm("primpath").set(primpath)
        add_var.setInput(1, graft)
        
        set_var = stage.createNode("setvariant")
        set_var.parm("variantset1").set("model")
        set_var.setInput(0, add_var)
        out_label = stage.createNode("null")
        out_label.setName(asset_name+"_OUT", 1)
        out_label.setInput(0, set_var)
        out_label.setDisplayFlag(True)

        stage.layoutChildren()

    def create_layout(self):
        stage = hou.node("/stage")

        ref1 = stage.createNode("reference")
        ref1.setName("empty_ref", 1)
        set_var1 = stage.createNode("setvariant")
        set_var1.setInput(0, ref1)
        edit1 = stage.createNode("edit")
        edit1.setInput(0, set_var1)

        ref2 = stage.createNode("reference")
        ref2.setName("empty_ref", 1)
        set_var2 = stage.createNode("setvariant")
        set_var2.setInput(0, ref2)
        edit2 = stage.createNode("edit")
        edit2.setInput(0, set_var2)

        merge = stage.createNode("merge")
        merge.setInput(0, edit1)
        merge.setInput(1, edit2)

        label = stage.createNode("null")
        label.setName("layout_OUT", 1)
        label.setInput(0, merge)
        label.setDisplayFlag(True)

        stage.layoutChildren()