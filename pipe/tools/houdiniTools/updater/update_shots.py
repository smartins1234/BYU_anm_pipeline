import hou, sys, os, shutil
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.shotgun import ShotgunReader
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.pipeHandlers import pipeline_io as pio

class UpdateShots:
    def __init__(self):
        self.project = Project()

    def update_shots(self):
        shot_list = ShotgunReader().getShotList()

        list_file = open(os.path.join(self.project.get_shots_dir(), ".shot_list"), "w")
        list_file.truncate(0)
        for shot in shot_list:
            list_file.write(shot + "\n")

            self.create_shot(shot)

        list_file.close()

        qd.message("Shots updated successfully.")

    def create_shot(self, shot):
        stage = hou.node("/stage")


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

        '''#set up a basic node network
        layout_box = stage.createNetworkBox()
        blue = hou.Color((.2, .4, .9))
        layout_box.setColor(blue)
        layout_box.setComment("layout")
        layout_out = stage.createNode("null")
        layout_out.setName("layout_OUT")
        layout_box.addNode(layout_out)

        anim_box = stage.createNetworkBox()
        red = hou.Color((.9, .2, .2))
        anim_box.setColor(red)
        anim_box.setComment("animation")
        anim_out = stage.createNode("null")
        anim_out.setName("animation_OUT")
        anim_box.addNode(anim_out)

        light_box = stage.createNetworkBox()
        yellow = hou.Color((1.0, 1.0, 0.1))
        light_box.setColor(yellow)
        light_box.setComment("lights")
        light_out = stage.createNode("null")
        light_out.setName("light_OUT")
        light_box.addNode(light_out)

        fx_box = stage.createNetworkBox()
        green = hou.Color((0.2, 0.9, 0.4))
        fx_box.setColor(green)
        fx_box.setComment("FX")
        fx_out = stage.createNode("null")
        fx_out.setName("FX_OUT")
        fx_box.addNode(fx_out)

        merge = stage.createNode("merge")
        merge.setInput(0, layout_out)
        merge.setInput(1, anim_out)
        merge.setInput(2, light_out)
        merge.setInput(3, fx_out)

        out = stage.createNode("null")
        out.setInput(0, merge)
        out.setName(shot + "_OUT")
        out.setDisplayFlag(True)

        stage.layoutChildren()'''
