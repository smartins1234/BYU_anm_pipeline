import hou, os
import pipe.pipeHandlers.quick_dialogs as qd

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset, Shot, AssetType
from pipe.pipeHandlers.element import Element

class Assembler:
    def __init__(self):
        self.default_ignored_folders = ["Asset Controls"]

    '''
        Creates new content HDAs
        @param asset_name: name of the asset to assemble/clone
        @param already_tabbed_in_node: an hda where the new content hdas should be created. Typically None
    '''
    def create_hda(self, asset_name, body=None, selected_nodes=None):
        if body is None:
            body = self.body

        if not body.is_asset():
            qd.error("Must be an Asset type.")
        type = body.get_type()

        if type is None:
            qd.error("Invalid body type specified.")
            return None


        if body.get_type() == AssetType.ASSET:
            node = self.build_asset(body, selected_nodes=selected_nodes)
        elif body.get_type() == AssetType.SHOT:
            return None
        else:
            qd.error("Pipeline error: this asset isn't an asset or a shot.")

        return node


    '''
        Build the node network for an Asset in an HDA subnet.
    '''
    def build_asset(self, body, selected_nodes=None):
        stage = hou.node("/stage")
        temp_node = stage.createNode("subnet")
        temp_node.deleteItems(temp_node.children())
        asset_name = body.get_name()

        HDA = temp_node.createDigitalAsset(
          name = asset_name,
          hda_file_name = os.path.join(body.get_filepath(), "hda", asset_name + ".hda"),
          description = body.get_type(),
          min_num_inputs = 0,
          max_num_inputs = 0,
        )
        HDA.setName(asset_name, unique_name=True)
        HDA.setDisplayFlag(True)

        #clean slate HDA is now created and ready to fill
        sop_create = HDA.createNode("sopcreate", "import_geo")
        sop_create.parm("enable_pathattr").set(True)
        sop_create.parm("enable_kindschema").set(True)
        sop_create.parm("enable_subsetgroups").set(True)
        sop_create.parm("kindschema").set("Nested assembly, groups, and components")
        sop_create.parm("subsetgroups").set("*")
        sop_create.setDisplayFlag(True)
        sop_view = sop_create.children()[0].children()[0]

        '''create import nodes if no hda exists'''
        if selected_nodes == None:
            usd_import = sop_view.createNode("usdimport")
            usd_import.parm("input_unpack").set(True)
            usd_import.parm("pathattrib").set("")
            element = Element(os.path.join(body.get_filepath(), "geo")).get_last_publish()
            if not element == None:
                print(element)
                print("\n\nImport filepath:  " + element[3])
                usd_import.parm("filepath1").set(element[3])
            wrangle = sop_view.createNode("attribwrangle")
            wrangle.setInput(0, usd_import, 0)
            wrangle.parm("snippet").set("s@path = \"/" + asset_name + "\";")
            wrangle.parm("class").set(1)

            output = sop_view.createNode("output")
            output.setInput(0, wrangle, 0)
            output.setDisplayFlag(True)
            output.setRenderFlag(True)
        else:
            hou.moveNodesTo(selected_nodes, sop_view)

        #childs = sop_create.children()[0].children()[0]
        sop_create.children()[0].layoutChildren()

        return HDA
