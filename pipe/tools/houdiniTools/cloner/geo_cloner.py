import hou
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class GeoCloner:
    
    def __init__(self):
        self.project = Project()

    def clone(self):
        asset_list = self.project.list_existing_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        print("Selected asset: " + value[0])
        filename = value[0]

        self.body = Project().get_body(filename)
        self.element = self.body.get_element(Asset.GEO)
        if self.element:
            #just reference in the asset, make sure we're referencing the usda geo
            path = self.element.get_last_publish()[3]
            parts = path.split(".")
            path = parts[0] + ".usda"

            ref = hou.node("/stage").createNode("reference")
            ref.setName(filename+"_geo", 1)
            ref.parm("filepath1").set(path)
        else:
            qd.error("Nothing was cloned")