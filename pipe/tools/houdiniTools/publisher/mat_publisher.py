import hou, os, re

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

'''
publishes materials as hda and usda files
'''
class MaterialPublisher:
    def __init__(self):
        self.project = Project()

    def publish(self):
        asset_list = self.project.list_assets()

        self.item_gui = sfl.SelectFromList(
            l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to publish")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        self.asset_name = value[0]

        body = Project().get_asset(self.asset_name)
        if not body:
            body = self.project.create_asset(self.asset_name)
        if not body:
            qd.error("Something broke :'(")
            return
        self.element = body.get_element(Asset.MATERIALS)

        self.path = os.path.join(self.element._filepath, "temp.usda")

        selection = hou.selectedNodes()
        if len(selection) != 1:
            qd.error("Please select only the material node and try again.")
            return
        shader = selection[0]
        if shader.type().name == "materiallibrary":
            qd.error("Changes have been made to this publishing tool. Now you must select the material node itself, NOT the material library, to publish it. Please try again.")
            return

        #check where we are and move shader node accordingly
        deleteLib = False
        path = shader.path()
        first = path.split("/")[1]
        if first != "stage":
            lib = hou.node("/stage").createNode("materiallibrary")
            deleteLib = True
            shader = hou.copyNodesTo([shader], lib)[0]
        else:
            lib = shader.parent()

        lib.setInput(0, None)
        lib.parm("matpath1").set(value[0])
        
        #create and save material hda
        if shader.canCreateDigitalAsset():
            hdaPath = os.path.join(self.element._filepath, self.asset_name + "_main.hda")
            shader = shader.createDigitalAsset(
                name = re.sub(r'\W+', '', self.asset_name),
                description=self.asset_name,
                hda_file_name=hdaPath,
                min_num_inputs=0,
                max_num_inputs=0
            )
            shaderDef = shader.type().definition()
            shaderOptions = shaderDef.options()
            shaderOptions.setUnlockNewInstances(True)
            shaderOptions.setSaveInitialParmsAndContents(True)
            shaderDef.setOptions(shaderOptions)
            shaderDef.save(hdaPath, shader, shaderOptions)
        elif shader.type().name() == re.sub(r'\W+', '', self.asset_name):
            shader.type().definition().updateFromNode(shader)
            shader.type().definition().save(shader.type().definition().libraryFilePath())
        else:
            qd.error("Error creating/saving hda. Continuing to save USDA...")
        

        shader.setName(value[0])

        rop = hou.node("/stage").createNode("usd_rop")
        rop.setInput(0, lib)
        rop.parm("lopoutput").set(self.path)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
        rop.parm("execute").pressButton()

        rop.destroy()
        if deleteLib:
            lib.destroy()

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
        name = self.asset_name

        self.element.update_app_ext(".usda")
        self.element.publish(username, self.path, comment, name)