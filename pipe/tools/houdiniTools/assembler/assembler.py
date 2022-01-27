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
            element = body.get_element(Asset.HDA)
            if element.get_last_version() < 0:
                path = os.path.join(element._filepath, asset_name + ".hda")
            else:
                path = element.get_last_publish()[3]

            node = self.build_asset(body, path, selected_nodes=selected_nodes)
        elif body.get_type() == AssetType.SHOT:
            return None
        else:
            qd.error("Pipeline error: this asset isn't an asset or a shot.")

        return node


    '''
        Build the node network for an Asset in an HDA subnet.
    '''
    def build_asset(self, body, path, selected_nodes=None):
        stage = hou.node("/stage")
        obj = hou.node("/obj")
        temp_node = obj.createNode("subnet")
        temp_node.deleteItems(temp_node.children())
        asset_name = body.get_name()

        HDA = temp_node.createDigitalAsset(
          name = "byu::" + asset_name,
          hda_file_name = path,
          description = "asset",
          min_num_inputs = 0,
          max_num_inputs = 0,
          version="0.0"
        )
        HDA.setName(asset_name, unique_name=True)
        HDA.setDisplayFlag(True)
        HDA.setColor(hou.Color((0.2,0.0,0.8)))

        geo = HDA.createNode("geo", asset_name)
        if self.add_spare_parameters(geo):
            geo.parm("rendersubd").set(True)

        import_geo = geo.createNode("file", "import_geo")
        element = Element(os.path.join(body.get_filepath(), "geo")).get_last_publish()
        if element:
            import_geo.parm("file").set(element[3])
        out = geo.createNode("null", "OUT_" + asset_name)
        out.setInput(0,import_geo, 0)
        out.setDisplayFlag(True)
        out.setRenderFlag(True)
        out.setColor(hou.Color((0.2,0.2,0.2)))

        geo.layoutChildren()

        return HDA

    def add_spare_parameters(self, target):
        vtuple = hou.applicationVersion()
        rfhtree = hou.getenv("RFHTREE")
        renderobjnames = ["geo"]
        rendercamnames = ["cam"]

        if target.type().name() in renderobjnames:
            path = rfhtree + "/18.5.351/soho/parameters/geoparms.ds"
        elif target.type().name() in rendercamnames:
            path = rfhtree + "/18.5.351/soho/parameters/camparms.ds"
        else:
            return None

        grp = target.parmTemplateGroup()
        spareparms = hou.ParmTemplateGroup()
        with open(path) as file:
            ds = file.read()
            spareparms.setToDialogScript(ds)
        for template in spareparms.parmTemplates():
            grp.append(template)

        try:
            target.parmsInFolder(("RenderMan",))
        except:
            target.setParmTemplateGroup(grp)

        if target.type().name() == "geo":
            hou.hscript("opproperty %s prman23geo *" % target.path())
        elif target.type().name() == "cam":
            hou.hscript("opproperty %s prman23cam *" % target.path())
