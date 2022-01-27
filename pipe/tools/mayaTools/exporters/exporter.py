import os
import pymel.core as pm

from pipe.pipeHandlers.project import Project
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.tools.mayaTools.utilities.utils import *
from pipe.tools.mayaTools.exporters.alembic_exporter import AlembicExporter
from pipe.tools.mayaTools.exporters.obj_exporter import ObjExporter
from pipe.tools.mayaTools.exporters.mb_exporter import MbExporter
from pipe.tools.mayaTools.exporters.usd_exporter import USDExporter
import pipe.pipeHandlers.select_from_list as sfl


class Exporter:

    def __init__(self):
        pass

    def go(self, alembic=False, usd=False, obj=False, mb=False, camera=False):
        self.alembic = alembic
        self.usd = usd
        self.obj = obj
        self.mb = mb
        self.camera = camera

        self.project = Project()
        self.chosen_asset = None

        if self.camera and self.alembic:    #previs publish case
            shot_list = self.project.list_shots()

            self.item_gui = sfl.SelectFromList(l=shot_list, parent=maya_main_window(), title="What shot is this camera in?")
            self.item_gui.submitted.connect(self.shot_results)

        else:
            asset_list = self.project.list_assets()

            self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to export to")
            self.item_gui.submitted.connect(self.asset_results)

    def export(self):
        publish_info = []
        if self.obj:    #modeling publish case
            publish_info.append(ObjExporter().exportSelected(self.chosen_asset))
            #self.publish(publish_info)

            if self.usd:    #modeling publish case
                publish_info.append(USDExporter().exportSelected(self.chosen_asset))
                self.publish(publish_info)

        if self.alembic:#animation publish case
            shot_list = self.project.list_shots()

            self.item_gui = sfl.SelectFromList(l=shot_list, parent=maya_main_window(), title="What shot is this animation in?")
            self.item_gui.submitted.connect(self.shot_results)

        if self.mb:     #rigging publish case
            publish_info.append(MbExporter().export(self.chosen_asset))
            self.publish(publish_info)

    def asset_results(self, value):
        self.chosen_asset = value[0]

        #check if asset already exists
        #if not, create it
        self.project.create_asset(name=self.chosen_asset)

        self.export()

    def shot_results(self, value):
        self.chosen_shot = value[0]
        print(self.chosen_shot)

        shot = self.project.create_shot(self.chosen_shot)

        #if the shot didn't exist already, set the frame range
        if shot is not None:    
            pass

        else:
            print("we're here")
            shot = self.project.get_shot(self.chosen_shot)

        if shot is None:
            print("uh oh stinky")
            return

        #pre-vis publish
        publish_info = []
        if self.camera:     
            camera_num = int(shot.get_camera_number())
            if camera_num == 1:     #only one camera in the shot
                self.chosen_asset = "camera1"
                publish_info.append(AlembicExporter().exportSelected(asset_name=self.chosen_asset, shot_name=self.chosen_shot, camera=self.camera))
                self.publish(publish_info)
            else:                   #pick which camera to publish
                cam_list = []
                for number in range(1, camera_num+1):
                    camera_name = "camera" + str(number)
                    cam_list.append(camera_name)

                self.item_gui = sfl.SelectFromList(l=cam_list, parent=maya_main_window(), title="Which camera are you publishing?")
                self.item_gui.submitted.connect(self.camera_results)

        #animation publish
        else:
            publish_info.append(AlembicExporter().exportSelected(asset_name=self.chosen_asset, shot_name=self.chosen_shot, camera=self.camera))
            self.publish(publish_info)

    def camera_results(self, value):
        publish_info = []
        self.chosen_asset = value[0]
        publish_info.append(AlembicExporter().exportSelected(asset_name=self.chosen_asset, shot_name=self.chosen_shot, camera=self.camera))
        self.publish(publish_info)

    def publish(self, publishes):
        publish_info = publishes[0]

        element = publish_info[0]
        path = publish_info[1]

        self.publishes = element.list_publishes()
        publishes_string_list = ""
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label

        # get comment and update element file with publish info
        comment = qd.input(title="Comment for publish", label=publishes_string_list)
        if comment is None or comment == "":
            comment = "No comment."
        username = Environment().get_user().get_username()

        for pub_info in publishes:
            element = pub_info[0]
            path = pub_info[1]
            element.publish(username, path, comment, self.chosen_asset)