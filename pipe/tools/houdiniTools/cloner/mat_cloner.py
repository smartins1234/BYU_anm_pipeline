import hou, re
from pxr import Usd, UsdShade, Sdf, Gf
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

'''
pulls materials into the context the user is in
'''
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
                createNewRef = True
                for child in hou.node("/stage").children():
                    if child.name() == filename+"_material_ref" and child.parm("filepath1").eval() == path:
                        child.parm("reload").pressButton()
                        createNewRef = False
                if createNewRef:
                    ref = hou.node("/stage").createNode("reference")
                    ref.setName(filename+"_material_ref", 1)
                    ref.parm("filepath1").set(path)
                    ref.parm("primpath").set("/materials/")

                panes = self.getCurrentNetworkEditorPane()
                paths = []
                for pane in panes:
                    paths.append(pane.pwd())

                hdaPath = path.split(".")[0] + ".hda"
                hou.hda.installFile(hdaPath)

                success = False

                for p in paths:
                    try:
                        for child in p.children():
                            if child.type().name() == re.sub(r'\W+', '', filename):
                                child.destroy()
                        newMat = p.createNode(re.sub(r'\W+', '', filename))
                        newMat.setName(filename, 1)
                        newMat.setMaterialFlag(True)
                        success = True
                    except:
                        pass

                if not success:
                    for child in hou.node("/mat").children():
                        if child.type().name() == re.sub(r'\W+', '', filename):
                            child.destroy()
                    newMat = hou.node("/mat").createNode(re.sub(r'\W+', '', filename))
                    newMat.setName(filename, 1)
                    newMat.setMaterialFlag(True)

                    qd.message("Material successfully cloned into /mat context.")

        else:
            qd.error("Nothing was cloned")

    def getCurrentNetworkEditorPane(self):
        editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]
        return editors