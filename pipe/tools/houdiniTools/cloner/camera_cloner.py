import hou, os
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class CameraCloner:
    def __init__(self):
        self.project = Project()

    def clone(self):
        shot_list = self.project.list_existing_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone from")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        self.shot_name = value[0]
        self.shot = self.project.get_shot(self.shot_name)
        element = self.shot.get_element(Asset.CAMERA)

        asset_list = next(os.walk(element._filepath))[1]
        for name in asset_list:
            if name == "cache":
                asset_list.remove(name)
        asset_list.sort(key=unicode.lower)

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an camera to clone")
        self.item_gui.submitted.connect(self.camera_results)

    #this could use some more testing once there's more cameras published
    def camera_results(self, value):
        camera_name = value[0]
        element = self.shot.get_element(os.path.join(Asset.CAMERA, camera_name))

        if element.get_last_version < 0:
            qd.error("There are no publishes for this camera.")
            return
        path = element.get_last_publish()[3]
        '''
        stage = hou.node("/stage")
        ref = stage.createNode("reference")
        ref.setName(camera_name + "_1", 0)
        ref.parm("filepath1").set(path)
        ref.parm("primpath").set("/camera/" + camera_name)
        '''
        cameraNode = hou.node("/obj").createNode("cenoteCamera")
        cameraNode.setName(self.shot_name + "_camera", 1)
        cameraNode.parm("fileName").set(path)
        cameraNode.parm("scale").set(0.01)
        cameraNode.parm("buildHierarchy").pressButton()