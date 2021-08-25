import hou
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class MaterialCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        asset_list = self.project.list_existing_assets()

        self.item_gui = sfl.SelectFromList(
            l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset's material to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        print("Selected asset: " + value[0])
        filename = value[0]

        self.body = Project().get_body(filename)
        self.element = self.body.get_element(Asset.MATERIALS)
        if self.element.get_last_version() >= 0:
            path = self.element.get_last_publish()[3]
            if path:
                ref = hou.node("/stage").createNode("reference")
                ref.setName(filename+"_material_ref", 1)
                ref.parm("filepath1").set(path)
                ref.parm("primpath").set("/materials/")

        else:
            qd.error("Nothing was cloned")