import hou
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment

'''
opens a shot's hip file, but only if it's not checked out already by another user
'''
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
        if self.element.get_last_version() >= 0:
            #check if checked out
            if self.element.is_assigned():
                assigned_user = self.element.get_assigned_user()
                username = Environment().get_user().get_username()
                if not assigned_user == username:
                    qd.error("This shot is currently checked out by " + assigned_user)
                    return
            else:
                username = Environment().get_user().get_username()
                self.element.update_assigned_user(username)

            path = self.element.get_last_publish()[3]
            if path:
                hou.hipFile.load(path)

        else:
            qd.error("Nothing was cloned")