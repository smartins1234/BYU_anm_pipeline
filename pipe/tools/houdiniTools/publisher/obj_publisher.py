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
publishes geometry from the obj context as obj and usda files
'''
class ObjPublisher:
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
        self.element = body.get_element(Asset.GEO)
        self.usdElem = body.get_element(Asset.GEO)
        path = self.element._filepath


        selectedNodes = hou.selectedNodes()
        if len(selectedNodes) != 1:
            qd.error("Select one node to publish its geometry")
            return
        geo = selectedNodes[0]
        if geo.type().name() != "geo":
            qd.error("You can only publish from geo nodes")
            return

        for child in geo.children():
            if child.isDisplayFlagSet():
                #print("hello there from " + child.name())
                cache = geo.createNode("filecache")
                cache.setInput(0, child)
                usd = geo.createNode("usdexport")
                usd.setInput(0, child)

                cache.parm("filemode").set(2)
                cache.parm("file").set(os.path.join(path, "temp.obj"))
                cache.parm("trange").set(0)
                cache.parm("execute").pressButton()

                usd.parm("authortimesamples").set("Never")
                usd.parm("lopoutput").set(os.path.join(path, "temp.usda"))
                usd.parm("execute").pressButton()

                usd.destroy()
                cache.destroy()

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
        basePath = self.element._filepath

        #usdElem = self.element.deepcopy()

        path = os.path.join(basePath, "temp.obj")
        self.element.update_app_ext(".obj")
        self.element.publish(username, path, comment, name)

        path = os.path.join(basePath, "temp.usda")
        self.usdElem.update_app_ext(".usda")
        self.usdElem.publish(username, path, comment, name)