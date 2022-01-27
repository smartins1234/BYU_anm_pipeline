from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.project import Element
from pipe.tools.mayaTools.utilities.utils import *

import maya.cmds as mc

'''
Opens maya files used by the Animation department.
'''
class ShotOpener:
    def __init__(self):
        self.project = Project()

    def open(self, quick=True):
        self.quick = quick
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=maya_main_window(), title="Select a shot to open")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        shot_name = value[0]
        self.name = shot_name

        shot = self.project.get_shot(shot_name)
        element = None
        try:
            element = shot.get_element(Asset.MAYA)
        except:
            element = shot.create_element(Asset.MAYA, Element.DEFAULT_NAME)

        if element.get_last_version() >= 0 and self.quick:
            filepath = element.get_last_publish()[3]
            print(filepath)
            mc.file(filepath, o=True, f=True)
        elif element.get_last_version() >=0 and not self.quick:
            self.element = element
            self.publishes = element.list_publishes()

            if not self.publishes:
                qd.error("There have been no publishes in this department.")
                return

            # make the list a list of strings, not tuples
            self.sanitized_publish_list=[]
            for publish in self.publishes:
                label=publish[0] + " " + publish[1] + " " + publish[2]
                self.sanitized_publish_list.append(label)

            self.item_gui = sfl.SelectFromList(
                l=self.sanitized_publish_list, parent=maya_main_window(), title="Select a version to open")
            self.item_gui.submitted.connect(self.version_results)
            
        else:
            qd.error("There's no maya file published for this shot.")

    def version_results(self, value):
        selected_publish=None
        for item in self.sanitized_publish_list:
            if value[0] == item:
                selected_publish=item

        selected_scene_file=None
        position = 0
        for publish in self.publishes:
            label=publish[0] + " " + publish[1] + " " + publish[2]
            if label == selected_publish:
                version_path = self.element.get_version_dir(position)
                version_path = os.path.join(version_path, self.name + ".mb")
                selected_scene_file = version_path
                break
            position += 1

        print(selected_scene_file)
        mc.file(selected_scene_file, o=True, f=True)
        
