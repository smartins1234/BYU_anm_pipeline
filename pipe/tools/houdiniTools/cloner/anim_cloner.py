import hou, os, re
from pxr import Usd, UsdShade, Sdf, Gf
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

'''
Pulls animations into the obj context and assigns the corresponding materials
'''
class AnimCloner:
    def __init__(self):
        self.project = Project()

    def clone(self):
        shot_list = self.project.list_existing_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone from")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        self.shot_name = value[0]
        self.shot = self.project.get_shot(self.shot_name)
        element = self.shot.get_element(Asset.ANIMATION)

        asset_list = next(os.walk(element._filepath))[1]
        for name in asset_list:
            if name == "cache":
                asset_list.remove(name)
        asset_list.sort(key=unicode.lower)

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to clone")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        self.asset_name = value[0]
        element = self.shot.get_element(os.path.join(Asset.ANIMATION, self.asset_name))

        if element.get_last_version < 0:
            qd.error("There are no publishes for this asset in this shot.")
            return
        path = element.get_last_publish()[3]
        self.build_network(path)

    def build_network(self, path):
        animNode = hou.node("/obj").createNode("cenoteAnimation")
        animNode.setName(self.asset_name + "_anim", 1)
        animNode.parm("fileName").set(path)
        animNode.parm("scale").set(0.01)
        animNode.parm("buildHierarchy").pressButton()
        #animNode.parm("rendersubd").set(True)

        matPath = self.getMatPath()
        hdaPath = matPath.split(".")[0]+".hda"
        if os.path.exists(hdaPath):
            hou.hda.installFile(hdaPath)
            for child in hou.node("/mat").children():
                if child.type().name() == re.sub(r'\W+', '', self.asset_name):
                    child.destroy()
            newMat = hou.node("/mat").createNode(re.sub(r'\W+', '', self.asset_name))
            newMat.setName(self.asset_name, 1)
            newMat.setMaterialFlag(True)

            animNode.parm("materialPath").set("/mat/"+newMat.name())
        else:
            qd.error("The material for " + self.asset_name + " needs to be republished before it can be cloned in. Republish the material and try again.")

    def getMatPath(self):
        asset = self.project.get_asset(self.asset_name)
        element = asset.get_element(Asset.MATERIALS)
        if element.get_last_version() < 0:
            return os.path.join(element._filepath, self.asset_name + "_main.usda")
        path = element.get_last_publish()[3]
        return path