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
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers import quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.environment import Environment

class MbExporter:
    def __init__(self, frame_range=1, gui=True, element=None, show_tagger=False):
        pm.loadPlugin("objExport")

    def asset_results(self, value):
        print("in asset_results")
        chosen_asset = value[0]
        print(chosen_asset)
        self.exportSelected(chosen_asset)

    def export(self, assetName):

        path = self.getFilePath(assetName)

        command = self.buildMbCommand(path)

        pm.Mel.eval(command)

        publish_info = []
        publish_info.append(self.element)
        publish_info.append(path)

        return publish_info

    def exportSelected(self, assetName):
        pass

    def buildMbCommand(self, outFilePath):
        command = "file -force -options \"v=0;\" -type \"mayaBinary\" -pr -ea \"" + outFilePath + "\""
        print(command)
        return command

    def getFilePath(self, name):
        asset = Project().get_asset(name)
        path = asset.get_filepath()
        path = os.path.join(path, Asset.RIG)

        self.element = asset.get_element(Asset.RIG)

        path = os.path.join(path, name)
        last_version = self.element.get_last_version()
        current_version = last_version + 1
        path = path + "_v" + str(current_version).zfill(3) + ".mb"
        print(path)
        return path