from pipe.pipeHandlers import *
from pipe.pipeHandlers import quick_dialogs
import os
from os import walk
import shutil

import maya.cmds as mc
import pymel.core as pm

import pipe.pipeHandlers.pipeline_io as pio
from pipe.tools.mayaTools.utilities.utils import *
from pipe.pipeHandlers.environment import Environment
from pipeHandlers.body import Asset
#from pipe.pipeHandlers.environment import Department
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
#import pipe.pipeHandlers.tests as sfl
#from PySide2.QtCore import QObject, Signal, Slot

from pipe.pipeHandlers.environment import Environment

def passAlong(value):
    ObjExporter().asset_results(value)

class ObjExporter:
    def __init__(self, frame_range=1, gui=True, element=None, show_tagger=False):
        pm.loadPlugin("objExport")

    def asset_results(self, value):
        print("in asset_results")
        chosen_asset = value[0]
        print(chosen_asset)
        self.exportSelected(chosen_asset)

    def export(self):#, element, selection=None, startFrame=None, endFrame=None):

        project = Project()
        asset_list = project.list_assets()
        #asset_list = ["TEST"]

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to export to")
        self.item_gui.submitted.connect(passAlong)

    def exportSelected(self, assetName):
        
        path = self.getFilePath(assetName)

        command = self.buildObjCommand(path)

        pm.Mel.eval(command)

        comment = qd.input("Comment for publish")   # get comment and update element file with publish info
        if comment is None:
            comment = "No comment."
        username = Environment().get_user().get_username()
        self.element.publish(username, path, comment)
        
        return None

    def buildObjCommand(self, outFilePath):
        options = "\"groups=1;ptgroups=1;materials=0;smoothing=0;normals=1;\""  #this string determines the options for exporting an obj, where 1 is true and 0 is false
        command = "file -options " + options + " -typ \"OBJexport\" -es \"" + outFilePath + "\";"
        print(command)
        return command

    def getFilePath(self, name):
        asset = Project().get_asset(name)
        path = asset.get_filepath()
        path = os.path.join(path, Asset.GEO)

        self.element = Element(path)

        path = os.path.join(path, name)
        last_version = self.element.get_last_version()
        current_version = last_version + 1
        path = path + "_v" + str(current_version).zfill(3) + ".obj"
        print(path)
        return path


        """env = Environment()
        path = env.get_assets_dir() + name + "/" + Asset.GEO                      # get directory of the asset

        name = name + "_GEO"

        if not os.path.exists(path):
            os.mkdir(path)

        if len(os.listdir(path)) > 0:
            _, _, filenames = next(walk(path))                              # get list of files in the directory
            filenames = list(filter(lambda x:x.endswith(".obj"), filenames))# get only obj files
            if not filenames:
                version = 1
            else:
                filenames = [fname[(len(name)+2):-4] for fname in filenames]# isolate the version number
                lastVersion = max([int(num) for num in filenames])          # get the latest version number
        
                version = lastVersion + 1                                   # version of the file to be saved
        else:
            version = 1

        path = path + "/" + name + "_v" + str(version).zfill(3) + ".obj"
        print(path)
        return path"""
