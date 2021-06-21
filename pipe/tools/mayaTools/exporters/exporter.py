import os
import pymel.core as pm

from pipe.pipeHandlers.project import Project
#import pipe.pipeHandlers.checkbox_options as co
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.tools.mayaTools.utilities.utils import *
from pipe.tools.mayaTools.exporters.alembic_exporter import AlembicExporter
from pipe.tools.mayaTools.exporters.obj_exporter import ObjExporter
import pipe.pipeHandlers.select_from_list as sfl
# from pipe.tools.mayaTools.exporters.fbx_exporter import FbxExporter
# from pipe.tools.mayaTools.exporters.json_exporter import JSONExporter

class Exporter:

    def __init__(self):
        '''self.body = None
        self.item_gui = None
        self.list = ["alembic", "fbx", "json", "usd", "obj"]
        self.cameras = True'''

    def go(self, alembic=False, usd=False, obj=False):
        self.alembic = alembic
        self.usd = usd
        self.obj = obj

        project = Project()
        asset_list = project.list_assets()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to export to")
        self.item_gui.submitted.connect(self.asset_results)

    def auto_export_all(self):
        '''self.export()'''

    def export_one(self, alembic=False, fbx=False, json=False, usd=False, methods=None):
        '''self.export(alembic=alembic, fbx=fbx, json=json, usd=usd, methods=methods)'''

    def export(self, ):
        
        if self.obj:
            ObjExporter().exportSelected(self.chosen_asset)

        if self.usd:
            #export as usd
            pass

        if self.alembic:
            shot_list = Project().list_shots()
            print(shot_list)
            self.item_gui = sfl.SelectFromList(l=shot_list, parent=maya_main_window(), title="What shot is this animation in?")
            self.item_gui.submitted.connect(self.shot_results)

        '''if methods is None:
            methods = self.list

        asset_name = os.environ.get("DCC_ASSET_NAME")
        if not asset_name:
            qd.error("You must first create or clone an asset.")
            return

        self.body = Project().get_body(asset_name)

        if alembic:
            AlembicExporter().auto_export(asset_name, self.cameras)

        if self.body and self.body.is_asset():
            if json:
                if self.body.get_type() == AssetType.SET or self.body.get_type() == AssetType.SHOT:
                    json_export = JSONExporter()
                    json_export.go(self.body, self.body.get_type())
                else:
                    methods.remove("json")

            if fbx:
                if self.body.get_type() == AssetType.PROP or self.body.get_type() == AssetType.ACTOR:
                    FbxExporter().auto_export(asset_name)
                else:
                    methods.remove("fbx")

        if usd:
            print("USD isn't supported... yet :|")
            methods.remove("usd")

        if methods:
            qd.info("Successfully exported " + str(asset_name) + " as " + str(methods))
        else:
            qd.info("Nothing was exported.")'''

    def export_without_cameras(self):
        '''self.cameras = False
        self.export()'''

    def export_with_options(self):
        '''self.item_gui = co.CheckBoxOptions(parent=maya_main_window(), title="Select export methods:", options=self.list)
        self.item_gui.submitted.connect(self.export_results)'''

    def export_results(self, export_results):
        '''fbx = True
        alembic = True
        json = True
        usd = True
        methods=[]

        for item in export_results.items():
            if item[0] == "fbx":
                if item[1] is False:
                    fbx = False
                else:
                    methods.append("fbx")

            elif item[0] == "alembic":
                if item[1] is False:
                    alembic = False
                else:
                    methods.append("alembic")

            elif item[0] == "json":
                if item[1] is False:
                    json = False
                else:
                    methods.append("json")

            elif item[0] == "usd":
                if item[1] is False:
                    usd = False
                else:
                    methods.append("usd")

        self.export(alembic=alembic, fbx=fbx, json=json, usd=usd, methods=methods)'''
    
    def asset_results(self, value):
        self.chosen_asset = value[0]

        #check if asset already exists
        #if not, create it

        proj = Project()
        proj.create_asset(name=self.chosen_asset)

        self.export()

    def shot_results(self, value):
        chosen_shot = value[0]
        print(chosen_shot)

        #check if shot already exists
        #if not, create it

        proj = Project()
        proj.create_shot(chosen_shot)

        AlembicExporter().exportSelected(self.chosen_asset, chosen_shot)