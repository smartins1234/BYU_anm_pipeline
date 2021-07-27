# this class is useless since we decided we're not doing
# version control for each time someone edits the layout
# in maya. i'm just keeping it for reference :P

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


class UsdSaver:
    def __init__(self):
        pm.loadPlugin("mayaUsdPlugin")

    def go(self):
        #open the layer editor
        pm.Mel.eval("mayaUsdOpenUsdLayerEditor")

        qd.message("Select the USD file in the layer editor window, then hit OK")

        #check if file needs to be saved
        nts = pm.Mel.eval("mayaUsdLayerEditorWindow -q -ns")

        if nts == 0:
            qd.message("No changes were made to the layout. No changes have been saved.")
            return
        
        #save changes made to the layer
        pm.Mel.eval("mayaUsdLayerEditorWindow -e -sv")

    def publish(self):
        

        #get comment
        comment = qd.input(title="Comment for publish", label=publishes_string_list)