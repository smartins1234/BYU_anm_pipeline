from pipe.pipeHandlers import *
from pipe.pipeHandlers import quick_dialogs
import os
import shutil

import maya.cmds as mc
import pymel.core as pm

import pipe.pipeHandlers.pipeline_io as pio
from pipe.tools.mayaTools.utilities.utils import *
from pipe.pipeHandlers.environment import Environment
#from pipe.pipeHandlers.environment import Department
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl


class AlembicExporter:
    def __init__(self, frame_range=1):
        self.frame_range = frame_range
        pm.loadPlugin("AbcExport")

    def asset_results(self, value):
        chosen_asset = value[0]
        print(chosen_asset)


    def exportSelected(self, asset_name, shot_name, camera=False):

        self.shot_name = shot_name
        self.shot = Project().get_shot(shot_name)

        if self.shot is None:
            return None

        start_frame = 0
        frame_range = str(self.shot.get_frame_range())
        #This means there's been no cameras even published for this shot but they're trying to save an animation. shouldn't ever happen
        if int(frame_range) == 0 and not camera:
            qd.error("How are you publishing without a camera yet? Get that done, bestie.")
            return
        #if this is previs we need to know where to move the keyframes to
        if camera:
            #ask the artist what frame the shot starts at and make sure that's a valid input
            start_frame = qd.input("Enter the starting frame for this shot")
            if start_frame is None or start_frame == u'':
                qd.error("Invalid frame range. Try publishing again.")
                return
            start_frame = str(start_frame)
            if not start_frame.isdigit():
                qd.error("Invalid frame range. Try publishing again.")
                return
            
            #ask the artist for the last frame and make sure that's valid input
            #we'll do this every time in case the length of the shot changes
            end_frame = qd.input("Enter the last frame for this shot")
            if end_frame is None or end_frame == u'':
                qd.error("Invalid frame range. Try publishing again.")
                return
            end_frame = str(end_frame)
            if not end_frame.isdigit():
                qd.error("Invalid frame range. Try publishing again.")
                return

            #calculate the frame-range and save it to the shot's .body file
            frame_range = int(end_frame) - int(start_frame) + 1
            self.shot.set_frame_range(frame_range)

            #now move the keyframes and build the command
            timeChange = int(start_frame) - 1
            anim_curves = mc.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])  
            for each in anim_curves:  
                mc.keyframe(each, edit=True, relative=True, timeChange=-timeChange)

            path = self.getCameraPath(asset_name)
            command = self.buildAlembicCommand(path, uv=False)
                
        else:
            path = self.getFilePath(asset_name)
            command = self.buildAlembicCommand(path)
        

        cont = qd.yes_or_no("This asset is about to be saved with " + str(frame_range) + " frames. Is that correct?")
        if not cont:
            qd.error("Nothing was published.")
            return

        pm.Mel.eval(command)
        
        #now move the keyframes back for previs
        if camera:
            timeChange = int(start_frame) - 1
            anim_curves = mc.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])  
            for each in anim_curves:  
                mc.keyframe(each, edit=True, relative=True, timeChange=timeChange)

        publish_info = [self.element, path]
        return publish_info

    def buildAlembicCommand(self, path, uv=True):
        #get selected nodes
        selected = mc.ls(sl=True,long=True)
        nodes = ""
        for node in selected:
            nodes += node
            nodes += " "

        frame_range = str(self.shot.get_frame_range())

        options = "-frameRange -48 " + frame_range
        if uv:
            options += " -uvWrite -writeUVSets"
        options += " -worldSpace -dataFormat ogawa -root " + nodes + "-file " + path

        command = "AbcExport -verbose -j \"" + options +"\""
        print(command)
        return command

    def getFilePath(self, asset_name):
        path = self.shot.get_filepath()
        dept = os.path.join(Asset.ANIMATION, asset_name) #this is to make it so we can keep track of the versions of animations for each asset
        path = os.path.join(path, dept)

        #try to create the element if it doesn't exist
        self.element = self.shot.create_element(dept, Element.DEFAULT_NAME)
        #retrieve it if it does already
        if self.element is None:
            self.element = self.shot.get_element(dept)
            
        self.element.update_app_ext(".abc")

        path = os.path.join(path, asset_name)
        last_version = self.element.get_last_version()
        current_version = last_version + 1
        path = path + "_v" + str(current_version).zfill(3) + ".abc"
        print(path)
        return path

    def getCameraPath(self, camera_name):
        path = self.shot.get_filepath()
        dept = os.path.join(Asset.CAMERA, camera_name) #this is to make it so we can keep track of the versions of animations for each camera
        path = os.path.join(path, dept)

        #try to create the element if it doesn't exist
        self.element = self.shot.create_element(dept, Element.DEFAULT_NAME)
        #retrieve it if it does already
        if self.element is None:
            self.element = self.shot.get_element(dept)

        self.element.update_app_ext(".abc")

        path = os.path.join(path, camera_name)
        last_version = self.element.get_last_version()
        current_version = last_version + 1
        path = path + "_v" + str(current_version).zfill(3) + ".abc"
        print(path)
        return path
