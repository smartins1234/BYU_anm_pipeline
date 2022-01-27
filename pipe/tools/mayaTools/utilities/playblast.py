import maya.cmds as cmds
import maya.mel as mel
from pymel.core import *

import pipe.pipeHandlers.quick_dialogs as qd
from pipe.tools.mayaTools.utilities.utils import *

'''
sets options for and creates playblasts
'''
class playblast:
    def __init__(self):
        pass

    def go(self, previs=False):
        if previs:
            #viewport settings
            for elem  in  getPanel(typ="modelPanel") :
                print(elem)
                cmds.modelEditor(elem, edit=True, dtx=True)
                #cmds.modelEditor(elem, edit=True, dl="all")
                cmds.modelEditor(elem, edit=True, sdw=1)

        #more viewport settings
        mel.eval("setCameraNamesVisibility(true);")
        mel.eval("setCurrentFrameVisibility(true);")
        mel.eval("setFocalLengthVisibility(true);")
        mel.eval("setAnimationDetailsVisibility(false);")
        mel.eval("setCapsLockVisibility(false);")
        mel.eval("setCurrentContainerVisibility(false);")
        mel.eval("setFrameRateVisibility(false);")
        mel.eval("setHikDetailsVisibility(false);")
        mel.eval("ToggleMaterialLoadingDetailsHUDVisibility(false);")
        mel.eval("setObjectDetailsVisibility(false);")
        mel.eval("setParticleCountVisibility(false);")
        mel.eval("setPolyCountVisibility(false);")
        mel.eval("setSceneTimecodeVisibility(false);")
        mel.eval("setSelectDetailsVisibility(false);")
        mel.eval("setSymmetryVisibility(false);")
        mel.eval("setViewAxisVisibility(false);")
        mel.eval("setViewportRendererVisibility(false);")
        from maya.plugin.evaluator.CacheUiHud import CachePreferenceHud; CachePreferenceHud().set_value( False )
        mel.eval("optionVar -iv inViewMessageEnable (false);")
        mel.eval("optionVar -iv inViewEditorVisible (false);")

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
        cmds.setAttr("hardwareRenderingGlobals.maxHardwareLights", 16)
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

        startFrame = qd.input("Enter start frame")
        endFrame = qd.input("Enter end frame")

        command = "playblast -st " + startFrame + " -et " + endFrame + " -orn true -os -fo -fmt \"qt\" -c \"jpeg\" -qlt 100 -w 2048 -h 858 -p 100 -filename \"" + fileName + "\";"
        print(command)
        mel.eval(command)