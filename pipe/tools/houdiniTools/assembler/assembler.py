import hou, os
import pipe.pipeHandlers.quick_dialogs as qd

from pipe.pipeHandlers.project import Project

class Assembler:
    def __init__(self):
        self.default_ignored_folders = ["Asset Controls"]

    '''
        Creates new content HDAs
        @param asset_name: name of the asset to assemble/clone
        @param department_paths: a dictionary of department to existing hda filepaths to clone. None if assembling
        @param already_tabbed_in_node: an hda where the new content hdas should be created. Typically None
    '''
    def create_hda(self, asset_name, body=None, department_paths=None):
        if body is None:
            body = self.body

        if not body.is_asset():
            qd.error("Must be an Asset type.")
        type = body.get_type()

        if type is None:
            qd.error("Invalid body type specified.")
            return None


        print "Creating node for {0}".format(body.get_name)

        if body.get_type() == AssetType.ASSET:
            node = self.build_asset (body)
        elif body.get_type() == AssetType.SHOT:
            return None
        else:
            qd.error("Pipeline error: this asset isn't an asset or a shot.")

        return node


    '''
        Build the node network for an Asset.
    '''
    def build_asset(self, body):
        stage = hou.node("/stage")
        temp_node = stage.createNode("subnet")
        asset_name = body.get_name()

        HDA_node = temp_node.createDigitalAsset(
          name = asset_name,
          hda_file_name = os.path.join(body.get_filepath, "hda", asset_name + ".hdanc"),
          description = body.get_type,
          min_num_inputs = 0,
          max_num_inputs = 0,
        )
        HDA.setName()
