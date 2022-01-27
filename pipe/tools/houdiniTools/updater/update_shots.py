import hou, sys, os, shutil
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.shotgun import ShotgunReader
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.pipeHandlers import pipeline_io as pio

'''
updates the local list of shots from shotgrid and
creates any new shots
'''
class UpdateShots:
    def __init__(self):
        self.project = Project()

    def update_shots(self):
        shot_list = ShotgunReader().getShotList()
        #print(shot_list)

        list_file = open(os.path.join(self.project.get_shots_dir(), ".shot_list"), "w")
        list_file.truncate(0)
        for shot in shot_list:
            #print("shot " + shot) 
            list_file.write(shot + "\n")

            self.create_shot(shot)

        list_file.close()

        qd.message("Shots updated successfully.")

    def create_shot(self, shot):
        stage = hou.node("/stage")
        #print(shot)

        #check if there's already a shot hip file, and if so, don't do anything
        body = self.project.get_shot(shot)
        if not body:
            body = self.project.create_shot(shot)
        element = body.get_element(Asset.HIP)
        file_name = os.path.join(element._filepath, shot + "_main.hipnc")
        if os.path.exists(file_name) or element.get_last_version() >= 0:
            #don't save over work already done
            return

        #copy over the template file and publish it
        src = os.path.join(self.project.get_project_dir(), "template.hipnc")
        dst = os.path.join(element._filepath, "temp.hipnc")
        shutil.copyfile(src, dst)

        comment = "blank shot file"
        username = "auto-create"

        element.update_app_ext(".hipnc")
        element.publish(username, dst, comment, shot)