import hou, os
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

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
        stage = hou.node("/stage")
        subnet = stage.createNode("subnet")
        subnet.setName(self.asset_name, 1)

        sopnet = subnet.createNode("sopnet")
        netName = self.asset_name + "_anim"
        sopnet.setName(netName, 1)
        abc = sopnet.createNode("alembic")

        abc.parm("fileName").set(path)
        abc.parm("loadmode").set(1)
        abc.parm("polysoup").set(0)
        abc.parm("curveFilter").set(0)
        abc.parm("NURBSFilter").set(0)

        sopimport = subnet.createNode("sopimport")
        sopimport.parm("soppath").set(sopnet.path())
        sopimport.setDisplayFlag(True)
        sopimport.parm("asreference").set(1)
        sopimport.parm("primpath").set("/anim/" + self.asset_name)

        #now get and attach materials, no idea if any of this works, btw. I'll have to test it when there's some animations done
        matPath = self.getMatPath()
        lib = subnet.createNode("reference")
        lib.parm("filepath1").set(matPath)
        lib.parm("primpath").set("/anim/" + self.asset_name)
        assign = subnet.createNode("assignmaterial")
        assign.parm("primpattern1").set("/anim/" + self.asset_name)
        assign.parm("matspecpath1").set("/anim/" + self.asset_name + "/" + self.asset_name)
        
        sopimport.setInput(0, subnet.indirectInputs()[0])
        assign.setDisplayFlag(True)
        lib.setInput(0, sopimport)
        assign.setInput(0, lib)

        output = None
        for child in subnet.children():
            if child.name() == "output0":
                output = child
                break
        output.setInput(0, assign)
        output.setDisplayFlag(True)

        subnet.layoutChildren()

    def getMatPath(self):
        asset = self.project.get_asset(self.asset_name)
        element = asset.get_element(Asset.MATERIALS)
        if element.get_last_version() < 0:
            return os.path.join(element._filepath, self.asset_name + "_main.usda")
        path = element.get_last_publish[3]
        return path