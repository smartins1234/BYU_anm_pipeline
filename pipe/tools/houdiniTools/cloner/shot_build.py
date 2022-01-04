import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Asset
from pipe.tools.houdiniTools.cloner.anim_cloner import AnimCloner
from pipe.tools.houdiniTools.cloner.layout_unpacker import LayoutUnpacker

class BuildShot:

    def __init__(self):
        self.project = Project()

    def build(self):
        shot_list = self.project.list_existing_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        self.shot_name = value[0]
        self.shotBody = Project().get_body(self.shot_name)

        camElement = self.shotBody.get_element(Asset.CAMERA)
        asset_list = next(os.walk(camElement._filepath))[1]
        for name in asset_list:
            if name == "cache":
                asset_list.remove(name)
        asset_list.sort(key=unicode.lower)
        if len(asset_list) < 1:
            qd.error("There is no camera for this shot, so it cannot be built. Quitting build for shot " + self.shot_name + "...")
        elif len(asset_list) == 1:
            self.camResults(asset_list)
        else:
            self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select a camera to clone")
            self.item_gui.submitted.connect(self.camera_results)

    def camResults(self, value):
        camName = value[0]
        self.camElement = self.shotBody.get_element(os.path.join(Asset.CAMERA, camName))
        options = ["Animation", "Layout", "Lights", "FX"]
        valueGui = qd.CheckboxSelect(
            text="Select what to import from this shot", options=options, parent=hou.ui.mainQtWindow(), title="Shot Build Settings")
        valueGui.submitted.connect(self.options_results)

    def options_results(self, options):
        '''for op in options:
            print(op)'''
        anim = options[0]
        layout = options[1]
        lights = options[2]
        fx = options[3]

        isCamera = self.get_camera()
        if not isCamera:
            return

        if anim:
            isAnim = self.get_all_anim()
            if not isAnim:
                qd.message("There is no animation published for this shot. Continuing to build shot...")

        if layout:
            isLayout = self.get_layout()
            if not isLayout:
                qd.message("Couldn't clone the layout for this shot. Continuing to build shot...")

        self.sequence_name = self.shot_name[:1]
        self.sequence = self.project.get_sequence(self.sequence_name)

        if lights:
            isLights = self.get_lights()
            if not isLights:
                qd.message("Couldn't clone sequence lighting. Continuing to build shot...")

        if fx:
            self.get_fx()

        hou.node("/obj").layoutChildren()

        self.build_render()


    def get_camera(self):
        if self.camElement.get_last_version < 0:
            qd.error(
                "There is no camera for this shot, so it cannot be built. Quitting build for shot " + self.shot_name + "...")
            return False
        try:
            path = self.camElement.get_last_publish()[3]
            
            cameraNode = hou.node("/obj").createNode("cenoteCamera")
            cameraNode.setName(self.shot_name + "_camera", 1)
            cameraNode.parm("fileName").set(path)
            cameraNode.parm("scale").set(0.01)
            cameraNode.parm("buildHierarchy").pressButton()
            return True
        except Exception as e:
            print(e)
            return False

    def get_all_anim(self):
        animElement = self.shotBody.get_element(Asset.ANIMATION)
        asset_list = next(os.walk(animElement._filepath))[1]
        for name in asset_list:
            if name == "cache":
                asset_list.remove(name)
        asset_list.sort(key=unicode.lower)
        if len(asset_list) < 1:
            return False

        for asset in asset_list:
            self.get_anim(asset)
        return True


    def get_anim(self, asset):
        element = self.shotBody.get_element(os.path.join(Asset.ANIMATION, asset))
        if element.get_last_version() < 0:
            return False

        try:
            path = element.get_last_publish()[3]

            anim_cloner = AnimCloner()
            anim_cloner.asset_name = asset
            anim_cloner.build_network(path)
            return True

        except Exception as e:
            print(e)
            return False

    def get_layout(self):
        layout_element = self.shotBody.get_element(Asset.LAYOUT)
        path = os.path.join(layout_element._filepath, self.shot_name + ".usda")
        if not os.path.exists(path):
            print("Layout path doesn't exist")
            return False
        try:
            layoutUnpacker = LayoutUnpacker()
            layoutUnpacker.shot_name = self.shot_name
            layoutUnpacker.unpack(path)
            return True
        except Exception as e:
            print(e)
            return False

    def get_lights(self):
        lightElement = self.sequence.get_element(Asset.LIGHTS)
        if lightElement.get_last_version() < 0:
            return False

        path = lightElement.get_last_publish()[3]
        hou.hda.installFile(path)

        try:
            hda = hou.node("/obj").createNode("sequence_"+self.sequence_name+"_lights")
        except Exception as e:
            #qd.error("Couldn't create node of type " + name + ". You should still be able to tab in the node manually.")
            print(e)
            return False

        try:
            hda.setName(self.sequence_name+"_sequence_lights", 1)
        except:
            pass

        try:
            hda.allowEditOfContents()
        except:
            pass
        
        return True

    def get_fx(self):
        fxElement = self.sequence.get_element(Asset.HDA)
        fx_list = next(os.walk(fxElement._filepath))[1]
        for name in fx_list:
            if name == "cache":
                fx_list.remove(name)
        fx_list.sort(key=unicode.lower)

        for fx in fx_list:
            self.get_one_fx(fx)

    def get_one_fx(self, fx):
        element = self.sequence.get_element(os.path.join(Asset.HDA, fx))


        if element.get_last_version() < 0:
            return
        filepath = element.get_last_publish()[3]

        try:
            hou.hda.installFile(filepath)
        except Exception as e:
            print(e)
            return

        try:
            hda = hou.node("/obj").createNode(fx)
        except Exception as e:
            qd.error("Couldn't create node of type " + fx + ". You should still be able to tab in the node manually.")

        try:
            hda.setName(fx, 1)
        except:
            pass

        try:
            hda.allowEditOfContents()
        except:
            pass

    def build_render(self):
        ris = hou.node("/out").createNode("cenote_layered_render")
        ris.parm("frame1").set(1)
        ris.parm("frame2").set(self.shotBody.get_frame_range())
        ris.parm("frame3").set(2)

        selected = None
        root = hou.node('/')
        camera_nodes = root.recursiveGlob('*', hou.nodeTypeFilter.ObjCamera)
        for cam in camera_nodes:
            if "shot" in cam.name():
                selected = cam
        if not selected:
            qd.error("Error selecting camera for render. Will need to be done manually.")
        else:
            ris.parm("camera").set(selected.path())

        layers = self.build_layer_string()
        print(layers)
        ris.parm("render_layers").set(layers)

        ris.parm("build_rops").pressButton()

        for node in ris.children():
            if node.type().name() == "tractorsubmit_main":
                node.parm("job_title").set(self.shot_name+"_Test_Render")
            else:
                node.parm("override_camerares").set(True)
                old = node.parm("ri_display_0").unexpandedString()
                new = old.replace("render", "testRender")
                node.parm("ri_display_0").set(new)

    def build_layer_string(self):
        first = ""
        second = ""
        third = ""
        total = ""

        for node in hou.node("/obj").children():
            if node.type().name() == "cenoteAnimation":
                first = first + "[ " + node.name() + " ] "
            elif node.type().name() == "cenoteLayoutNet":
                third = third + node.name() + " "
            elif node.type().name() != "cenoteCamera" and not "sequence_lights" in node.name():
                second = second + node.name() + " "

        if len(first) > 0:
            total = total + first
        if len(second) > 0:
            total = total + "[ " + second + "] "
        if len(third) > 0:
            total = total + "[ " + third + "]"

        return total
        #build render setup
            #layers: anim, fx, layout
            #half res on 2's
            #selecting the right camera will be a butt

            #maybe add a preview render node (everything on one layer)

        #that SHOULD be it