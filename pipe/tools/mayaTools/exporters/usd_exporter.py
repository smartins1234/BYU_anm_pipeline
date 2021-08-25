from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.project import Asset
from pipe.pipeHandlers.project import Element
import os

import maya.cmds as mc
import pymel.core as pm

class USDExporter:

    def __init__(self):
        self.project = Project()
        pm.loadPlugin("mayaUsdPlugin")

    def save_usd(self, filepath, asset_name):
        # okay, so try to make a bash script that can open houdini in the background, then run a script that saves
        # the usd file and then publishes it (looks like using hython is a good bet, i think i could write a hython
        # script then run it from a bash script)
        print("please work")

    def exportSelected(self, assetName):

        path = self.getFilePath(assetName)

        command = self.buildUsdCommand(path, assetName)

        pm.Mel.eval(command)

        publish_info = []
        publish_info.append(self.element)
        publish_info.append(path+".usd")

        return publish_info

    def buildUsdCommand(self, outFilePath, assetName):

        # this string determines the options for exporting a usd, where 1 is true and 0 is false
        options = "\";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportColorSets=0;defaultMeshScheme=none;defaultUSDFormat=usda;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=1;frameStride=1;frameSample=0.0;exportDisplayColor=0;shadingMode=none;exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;stripNamespaces=0\""
        command = "file -options " + options + \
            " -typ \"USD Export\" -es \"" + outFilePath + "\";"
        print(command)
        return command

    def getFilePath(self, name):
        asset = Project().get_asset(name)
        path = asset.get_filepath()
        path = os.path.join(path, Asset.GEO)

        self.element = Element(path)
        self.element.update_app_ext(".usda")
        path = os.path.join(path, name)
        last_version = self.element.get_last_version()
        current_version = last_version + 1
        path = path + "_v" + str(current_version).zfill(3)# + ".usda"
        print(path)
        return path
