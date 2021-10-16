import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io as pio

class LayoutPublisher:

    def __init__(self):
        self.project = Project()

    def publish(self):
        if len(hou.selectedNodes()) != 1:
            qd.error("Select only the last node in the network")
            return

        layout_list = Project().list_layouts()

        self.item_gui = sfl.SelectFromList(l=layout_list, parent=hou.qt.mainWindow(), title="Which layout are you publishing?")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        self.layout_name = value[0]

        self.layout = self.project.get_layout(self.layout_name)
        if self.layout is None:
            self.layout = Project().create_layout(self.layout_name)
        if self.layout is None:
            qd.error("Stephanie done messed up")
            return

        self.element = self.layout.get_element(Asset.LAYOUT)

        rop = hou.node("/stage").createNode("usd_rop")

        out = hou.selectedNodes()[0]
        rop.setInput(0, out)

        self.savePath = os.path.join(self.element._filepath, self.layout_name + ".usda")
        rop.parm("lopoutput").set(self.savePath)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)

        rop.parm("execute").pressButton()

        rop.destroy()

        publishes = self.element.list_publishes()
        publishes_string_list = ""
        for publish in publishes:
            label = publish[0] + " " + publish[1] + " " + publish[2] + "\n"
            publishes_string_list += label
        
        self.comment = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment for publish?", info=publishes_string_list)
        self.comment.submitted.connect(self.comment_results)

    def comment_results(self, value):
        comment = str(value)
        username = Environment().get_user().get_username()
        self.element.update_app_ext(".usda")
        self.element.publish(username, self.savePath, comment, self.layout_name)

        if self.element.get_last_version() == 0:
            # if it is the first publish, we have to make the referencing file as well
            # create a reference node
            ref = hou.node("/stage").createNode("reference")
            # set the values to reference the main publish file, etc.
            ref.parm("primpath").set("/layout")
            ref.parm("filepath1").set(self.element.get_last_publish()[3])          
            # create a USD ROP node and connect it to the ref node
            refrop = hou.node("/stage").createNode("usd_rop")
            refrop.setInput(0, ref)
            # set the values in the ROP and save to disk alongside the main publish
            refrop.parm("lopoutput").set(os.path.join(self.element._filepath, self.layout_name + "_ref.usda"))
            refrop.parm("enableoutputprocessor_simplerelativepaths").set(0)
            refrop.parm("execute").pressButton()

            pio.set_permissions(os.path.join(self.element._filepath, self.layout_name + "_ref.usda"))
            #   this only needs to be done once since with every new publish, the file being referenced gets updated
            ref.destroy()
            refrop.destroy()