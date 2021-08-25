import hou, os, shutil
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
import pipe.pipeHandlers.pipeline_io as pio

class LayoutCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        shot_list = self.project.list_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone from")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
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
            self.item_gui.submitted.connect(self.layout_results)
            return

        self.load(path)

    def layout_results(self, value):
        layout_name = value[0]

        # copy ref file into the shot
        layout_body = self.project.get_layout(layout_name)
        element = layout_body.get_element(Asset.LAYOUT)
        src = os.path.join(element._filepath, layout_name + "_ref.usda")
        dst = os.path.join(self.layout_element._filepath, self.shot_name + ".usda")
        shutil.copy(src, dst)
        pio.set_permissions(dst)
        self.load(dst)

    def load(self, file):
        ref = hou.node("/stage").createNode("loadlayer")
        ref.setName("layout_ref", 1)
        ref.parm("filepath").set(file)

        ref.setDisplayFlag(True)

        rop = hou.node("/stage").createNode("usd_rop")
        rop.setInput(0, ref)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
        rop.parm("lopoutput").set(file)
        rop.setName("save_layout", 1)

        hou.node("/stage").layoutChildren()