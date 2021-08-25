import hou
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class ShotCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        shot_list = self.project.list_existing_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        print("Selected shot: " + value[0])
        shot_name = value[0]

        self.body = Project().get_body(shot_name)
        self.element = self.body.get_element(Asset.HIP)
        if self.element:
            path = self.element.get_last_publish()[3]
            if path:
                hou.hipFile.load(path)

        else:
            qd.error("Nothing was cloned")