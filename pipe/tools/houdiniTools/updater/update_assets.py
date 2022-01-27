import hou, sys, os, shutil
from pxr import Usd, UsdShade, Sdf

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io as pio
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.pipeHandlers.shotgun import ShotgunReader


def filter(string, substr):
    return [str for str in string if
             substr in string]

'''
gets list of assets from Shotgun Studio and creates them in the pipeline

where applicable, assets are automatically organized into variant sets
'''
class UpdateAssets:
    def __init__(self):
        self.project = Project()

    def update_assets(self):
        lists = ShotgunReader().getAssetLists()
        asset_list = lists[0]
        assets = lists[1]

        #update .asset_list
        list_file = open(os.path.join(self.project.get_assets_dir(), ".asset_list.txt"), "w")
        list_file.truncate(0)
        for name in asset_list:
            list_file.write(name + "\n")
        list_file.close()

        #update .short_asset_list
        list_file = open(os.path.join(self.project.get_assets_dir(), ".short_asset_list"), "w")
        list_file.truncate(0)
        
        for asset in assets:
            name = asset["name"]
            variants = asset["children"][:]
            print("name: "+name)
            print("variants: ",variants)

            self.build_asset(name, variants)

            list_file.write(name+"\n")

        list_file.close()

        qd.message("Assets updated successfully.")                


    def build_asset(self, main_name, variants):
        stage = hou.node("/stage")
        self.primpath = "/" + main_name

        prim = stage.createNode("primitive")
        prim.setName("base_prim", 1)
        prim.parm("primpath").set(self.primpath)

        config = stage.createNode("configurelayer")
        config.setName("set_default_prim", 1)
        config.setInput(0, prim)
        config.parm("defaultprim").set(self.primpath)
        config.parm("setdefaultprim").set(1)

        add_var = stage.createNode("addvariant")
        add_var.parm("primpath").set(self.primpath)

        in_count = 1

        for var in variants:
            self.add_variant(var, config, add_var, in_count)
            in_count += 1

        out_label = stage.createNode("null")
        out_label.setName(main_name+"_OUT", 1)
        out_label.setInput(0, add_var)

        #our asset is now assembled, and just needs to be published
        body = self.project.get_asset(main_name)
        if not body:
            qd.error("Error publishing asset " + main_name + ". Continuing to next asset.")
            return

        element = body.get_element(Asset.USD)
        element.update_app_ext(".usda")

        path = os.path.join(element._filepath, "temp.usda")

        rop = hou.node("/stage").createNode("usd_rop")
        rop.setInput(0, out_label)
        rop.parm("lopoutput").set(path)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
        rop.parm("execute").pressButton()

        stage.layoutChildren()


        comment = "Automatic publish"
        username = "auto_update"
        name = main_name

        element.publish(username, path, comment, name)

        for child in stage.children():
            child.destroy()
        
    def add_variant(self, var, config, add_var, in_count):
        stage = hou.node("/stage")

        ref1 = stage.createNode("reference")
        ref1.setName(var + "_geo", 1)
        ref1.parm("primpath").set(self.primpath)
        geo_path = self.getGeoPath(var)
        ref1.parm("filepath1").set(geo_path)

        disp = stage.createNode("rendergeometrysettings")
        disp.parm("xn__primvarsdisplacementboundsphere_control_n4br").set("set")
        disp.parm("xn__primvarsdisplacementboundsphere_mrbr").set(1)
        disp.setInput(0, ref1)
        
        lib1 = stage.createNode("reference")
        lib1.setInput(0, disp)
        lib1.parm("primpath").set("/materials/")
        mat_path = self.getMatPath(var)
        lib1.parm("filepath1").set(mat_path)

        mat_asgn = stage.createNode("assignmaterial")
        mat_asgn.setInput(0, lib1)
        mat_asgn.parm("primpattern1").set(self.primpath)
        usd_stage = mat_asgn.stage()
        mat_prim = usd_stage.GetPrimAtPath("/materials")
        shader_path = mat_prim.GetChildren()[0].GetPath()
        #print("SHADER PATH: " + str(shader_path))
        mat_asgn.parm("matspecpath1").set(str(shader_path))

        label = stage.createNode("null")
        label.setName(var + "_OUT", 1)
        label.setInput(0, mat_asgn)

        graft = stage.createNode("graftstages")
        graft.setName(var, 1)
        graft.parm("primpath").set(self.primpath)
        graft.parm("destpath").set("/")
        graft.setInput(0, config)
        graft.setInput(1, label)

        add_var.setInput(in_count, graft)

    def getGeoPath(self, var):
        body = self.project.get_asset(var)
        if not body:
            body = self.project.create_asset(var)

        element = body.get_element(Asset.GEO)
        if element.get_last_version() >= 0:
            return element.get_last_publish()[3]

        else:
            #copy over the blank usda file
            src = self.project.get_project_dir()
            src = os.path.join(src, "blank.usda")
            dst = os.path.join(element._filepath, var + "_main.usda")

            shutil.copyfile(src, dst)
            pio.set_permissions(dst)

            return dst

    def getMatPath(self, var):
        body = self.project.get_asset(var)
        if not body:
            body = self.project.create_asset(var)

        element = body.get_element(Asset.MATERIALS)
        myPath = os.path.join(element._filepath, var+"_main.usda")
        if os.path.exists(myPath):
            return myPath

        else:
            #create and publish a basic material, return the path
            dst = os.path.join(element._filepath, var + "_main.usda")

            mat_lib = hou.node("/stage").createNode("materiallibrary")
            pink = mat_lib.createNode("usdpreviewsurface")
            pink.setName(var)
            pink.parm("diffuseColorr").set(.6)
            pink.parm("diffuseColorg").set(.6)
            pink.parm("diffuseColorb").set(.6)

            rop = hou.node("/stage").createNode("usd_rop")
            rop.setInput(0, mat_lib)
            rop.parm("lopoutput").set(dst)
            rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
            rop.parm("execute").pressButton()

            mat_lib.destroy()
            rop.destroy()

            pio.set_permissions(dst)

            return dst