# TODO
# pull up shot list, have user choose
# if shot has no layout yet, make them choose one
# then
# do the thing, ig

from pipe.pipeHandlers import *
from pipe.pipeHandlers import quick_dialogs
import os
import shutil

import maya.cmds as mc
import pymel.core as pm

import pipe.pipeHandlers.pipeline_io as pio
from pipe.tools.mayaTools.utilities.utils import *
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl


class UsdReader:
    def __init__(self):
        pm.loadPlugin("mayaUsdPlugin")
        self.project = Project()

    def go(self, quick=True):
        self.quick = quick
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(
            l=shot_list, parent=maya_main_window(), title="Which shot is this layout in?")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        self.shot_name = value[0]
        self.shot = self.project.get_shot(self.shot_name)
        if not self.shot:
            self.shot = self.project.create_shot(self.shot_name)
        if not self.shot:
            qd.error("This is real :'( (but the shot you picked isn't. talk to stephanie)")

        self.element = self.shot.get_element(Asset.LAYOUT)

        if self.element is None:
            qd.warning("Nothing was cloned.")
            return

        if self.quick:
            path = os.path.join(self.element._filepath, self.shot_name+".usda")
            if os.path.exists(path):
                self.open_scene_file(path)
                return
            else:
                self.choose_layout()
                return
            '''latest = self.element.get_last_publish()
            if latest is None:
                self.choose_layout()
                return
            else:
                selected_scene_file = latest[3]
                self.open_scene_file(selected_scene_file)
                return'''

        self.publishes = self.element.list_publishes()

        if not self.publishes:
            self.choose_layout()
            return

        # make the list a list of strings, not tuples
        self.sanitized_publish_list = []
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2]
            self.sanitized_publish_list.append(label)

        self.item_gui =sfl.SelectFromList(
            l=self.sanitized_publish_list, parent=maya_main_window(), title="Select publish to clone")
        self.item_gui.submitted.connect(self.publish_selection_results)

    def publish_selection_results(self, value):

        selected_publish = None
        for item in self.sanitized_publish_list:
            if value[0] == item:
                selected_publish = item

        selected_scene_file = None
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2]
            if label == selected_publish:
                selected_scene_file = publish[3]

        # selected_scene_file is the one that contains the scene file for the selected commit
        self.open_scene_file(selected_scene_file)

    def open_scene_file(self, selected_scene_file):
        if selected_scene_file is not None:

            if not os.path.exists(selected_scene_file):
                qd.error(
                    "That publish is missing. It may have been deleted to clear up space.")
                return False

            else:
                # do the thing
                command = "mayaUsd_createStageFromFilePath(\"" + selected_scene_file + "\")"
                pm.Mel.eval(command)

            return True
        else:
            return False

    def choose_layout(self):
        layout_list = self.project.list_layouts()

        self.item_gui =sfl.SelectFromList(
            l=layout_list, parent=maya_main_window(), title="Select layout to clone")
        self.item_gui.submitted.connect(self.layout_results)

    def layout_results(self, value):
        layout_name = value[0]
        layout = self.project.get_layout(layout_name)
        layout_element = layout.get_element(Asset.LAYOUT)
        src = os.path.join(layout_element._filepath, layout_name + "_ref.usda")
        dst = os.path.join(self.element._filepath, self.shot_name + ".usda")

        shutil.copy(src, dst)
        pio.set_permissions(dst)

        # basically set up a fake publish since we're not doing version control on this file
        self.element._datadict[self.element.LATEST_VERSION] = 0
        timestamp = pio.timestamp()
        username = Environment().get_user().get_username()
        self.element._datadict[self.element.PUBLISHES].append((username, timestamp, "initial publish", dst))
        self.element._update_pipeline_file()

        self.open_scene_file(dst)

