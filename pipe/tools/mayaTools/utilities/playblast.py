import maya.cmds as cmds
import maya.mel as mel

import pipe.pipeHandlers.quick_dialogs as qd
from pipe.tools.mayaTools.utilities.utils import *

class playblast:
    def __init__(self):
        pass

    def go(self):
        selected = cmds.ls(sl=True,long=True)
        if len(selected) == 0:
            qd.error("Select the camera you're playblasting from")
            return

        myCam = selected[0]

        #camera settings
        cmds.setAttr(myCam+".displayResolution", True)
        cmds.setAttr(myCam+".displayGateMaskColor", 0, 0, 0, type="double3")
        cmds.setAttr(myCam+".displayGateMaskOpacity", 1.0)
        cmds.setAttr(myCam+".filmFit", 1)
        cmds.setAttr(myCam+".overscan", 1.0)

        
        # Unlock the render globals' current renderer attribute
        cmds.setAttr("defaultRenderGlobals.currentRenderer", l=False)    

        # Sets the current renderer to given renderer
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaHardware2", type="string")
        cmds.setAttr("defaultResolution.width", 2048)
        cmds.setAttr("defaultResolution.height", 858)
        cmds.setAttr("defaultResolution.aspectLock", True)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)
        cmds.setAttr("hardwareRenderingGlobals.ssaoSamples", 32)
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
        cmds.setAttr("hardwareRenderingGlobals.multiSampleCount", 16)

        # Deletes the render settings window UI completely
        if cmds.window("unifiedRenderGlobalsWindow", exists=True):
                cmds.deleteUI("unifiedRenderGlobalsWindow")

        # Remake the render settings UI
        mel.eval('unifiedRenderGlobalsWindow;')

        fileName = qd.chooseFile(parent=maya_main_window(), caption="Save playblast as: ")[0]
        print(fileName)

        if fileName[-4:] != ".mov":
            fileName += ".mov"

        command = "playblast -orn true -os -fo -fmt \"qt\" -c \"jpeg\" -qlt 100 -w 2048 -h 858 -p 100 -filename \"" + fileName + "\";"
        print(command)
        mel.eval(command)