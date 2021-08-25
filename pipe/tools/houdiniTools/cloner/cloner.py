import hou, os
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
import shutil

#from unpacker import Unpacker
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
import pipe.pipeHandlers.pipeline_io as pio


class Cloner:

    def __init__(self):
        self.item_gui = None
        self.modify_publish = None
        self.material_publish = None
        self.hair_publish = None
        self.cloth_publish = None
        environment = Environment()
        self.user = environment.get_user()

    def clone_tool(self, node=None):
        self.project = Project()
        hda_list = self.project.list_hdas()

        self.item_gui = sfl.SelectFromList(l=hda_list, parent=hou.ui.mainQtWindow(), title="Select a tool to clone")
        self.item_gui.submitted.connect(self.tool_results)

    def tool_results(self, value):
        tool_name = value[0]

        source = os.path.join(Environment().get_hda_dir(), str(tool_name) + ".hda")

        hou.hda.installFile(source)
        obj = hou.node("/obj")

        try:
            hda = obj.createNode(tool_name)
        except:
            try:
                out = hou.node("/out")
                hda = out.createNode(tool_name)
            except Exception as e:
                qd.error("Could not find the correct context for tool: " + str(tool_name), details=str(e))
                return

        definition = hou.hdaDefinition(hda.type().category(), hda.type().name(), source)
        definition.setPreferred(True)

        hda.allowEditingOfContents()

        try:
            hda.setName(tool_name)
        except:
            print(str(tool_name) + " cloned but could not be renamed correctly.")

        layout_object_level_nodes()

    def clone_shot(self):
        project = Project()

        asset_list = project.list_shots()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        shot_name = value[0]
        project = Project()

        body = project.get_body(shot_name)
        element = body.get_element("hip")

        self.publishes = element.list_publishes()
        print("publishes: ", self.publishes)

        '''if not self.publishes:
            # has not been imported. Import it first.
            importer = Importer()
            importer.import_shot([shot_name])
            return'''

        # make the list a list of strings, not tuples
        self.sanitized_publish_list = []
        for publish in self.publishes:
            path = publish[3]
            file_ext = path.split('.')[-1]
            if not file_ext == "hip" and not file_ext == "hipnc":
                continue
            label = publish[0] + " " + publish[1] + " " + publish[2]
            self.sanitized_publish_list.append(label)

        self.item_gui = sfl.SelectFromList(l=self.sanitized_publish_list, parent=hou.ui.mainQtWindow(), title="Select publish to clone")
        self.item_gui.submitted.connect(self.publish_selection_results)

    def publish_selection_results(self, value):

        selected_publish = None
        for item in self.sanitized_publish_list:
            if value[0] == item:
                selected_publish = item

        selected_scene_file = None
        for publish in self.publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2]
            if label == selected_publish:
                selected_scene_file = publish[3]

        if selected_scene_file is not None:
            if not os.path.exists(selected_scene_file):
                qd.error('Filepath doesn\'t exist', details="Publish may have been deleted to conserve space.")
                return
            else:
                hou.hipFile.load(selected_scene_file)

    def get_department_paths(self, body):
        self.modify_element = body.get_element("modify")
        self.material_element = body.get_element("material")
        self.hair_element = body.get_element("hair")
        self.cloth_element = body.get_element("cloth")

        self.filepath = body.get_filepath()

        modify_publish = self.modify_element.get_last_publish()
        material_publish = self.material_element.get_last_publish()
        hair_publish = self.hair_element.get_last_publish()
        cloth_publish = self.cloth_element.get_last_publish()

        if not modify_publish and not material_publish and not hair_publish and not cloth_publish:
            department_paths = None
        else:
            department_paths = {}

        if(modify_publish):
            self.modify_publish = modify_publish[3]
            department_paths['modify'] = self.modify_publish
        if(material_publish):
            self.material_publish = material_publish[3]
            department_paths['material'] = self.material_publish
        if(hair_publish):
            self.hair_publish = hair_publish[3]
            department_paths['hair'] = self.hair_publish
        if(cloth_publish):
            self.cloth_publish = cloth_publish[3]
            department_paths['cloth'] = self.cloth_publish

        return department_paths

    def clone_asset(self, solaris):
        project = Project()

        asset_list = project.list_existing_assets()
        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to clone")
        if solaris:
            self.item_gui.submitted.connect(self.solaris_asset_results)
        else:
            self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        print("Selected asset: " + value[0])
        filename = value[0]

        self.body = Project().get_body(filename)
        self.element = self.body.get_element(Asset.HDA)
        filepath = self.element.get_last_publish()[3]
        nodeType = "byu::" + filename

        hou.hda.installFile(filepath)
        node = hou.node("/obj").createNode(nodeType)
        node.setName(filename, unique_name=True)
        node.setDisplayFlag(True)
        node.setColor(hou.Color((0.2,0.0,0.8)))
        #department_paths = self.get_department_paths(self.body)

        '''from pipe.tools.houdiniTools.assembler.assembler import Assembler  # we put import here to avoid cross import issue #63 FIXME

        node =  Assembler().create_hda(filename, body=self.body)'''
        #layout_object_level_nodes()

        return node

    def solaris_asset_results(self, value):
        print("Selected asset: " + value[0])
        filename = value[0]

        self.body = Project().get_body(filename)
        self.element = self.body.get_element(Asset.GEO)
        if self.element:
            #just reference in the asset, make sure we're referencing the usda geo
            path = self.element.get_last_publish()[3]
            parts = path.split(".")
            path = parts[0] + ".usda"

            ref = hou.node("/stage").createNode("reference")
            ref.setName(filename, 1)
            ref.parm("filepath1").set(path)
        else:
            pass

    def clone_layout(self):
        # assume layout from specific shot
        self.project = Project()
        
        shot_list = self.project.list_shots()
        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone from")
        self.item_gui.submitted.connect(self.layout_results)

    def layout_results(self, value):
        self.shot_name = value[0]
        self.shot = self.project.get_shot(self.shot_name)
        if not self.shot:
            self.shot = self.project.create_shot(self.shot_name)
        if not self.shot:
            qd.error("Something's wrong here. Talk to Stephanie")
        self.layout_element = self.shot.get_element(Asset.LAYOUT)
        path = os.path.join(self.layout_element._filepath, self.shot_name + ".usda")
        if not os.path.exists(path):
            # no layout is associated with this shot yet
            layouts = self.project.list_existing_layouts()

            self.item_gui = sfl.SelectFromList(l=layouts, parent=hou.ui.mainQtWindow(), title="Select a layout for this shot")
            self.item_gui.submitted.connect(self.layouts_results)
            return

        self.create_ref(path)

    def layouts_results(self, value):
        layout_name = value[0]

        # copy ref file into the shot
        layout_body = self.project.get_layout(layout_name)
        element = layout_body.get_element(Asset.LAYOUT)
        src = os.path.join(element._filepath, layout_name + "_ref.usda")
        dst = os.path.join(self.layout_element._filepath, self.shot_name + ".usda")
        shutil.copy(src, dst)
        pio.set_permissions(dst)
        self.create_ref(dst)

    def unpack_usd(self, file):
        print(file)
        #Unpacker().unpack_usd2(file)

    def create_ref(self, file):
        layout_name = file.split("/")[-1][:-5]
        
        ref = hou.node("/stage").createNode("reference")
        ref.setName(layout_name + "_ref")
        ref.parm("filepath1").set(file)
        ref.parm("primpath").set("/shot/layout")
        ref.setDisplayFlag(True)