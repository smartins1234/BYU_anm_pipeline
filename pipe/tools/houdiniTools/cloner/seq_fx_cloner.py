import hou, os

import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
import pipe.pipeHandlers.pipeline_io as pio

class FXCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        sequence_list = self.project.list_sequences()

        self.item_gui = sfl.SelectFromList(
            l=sequence_list, parent=hou.ui.mainQtWindow(), title="Select a sequence")
        self.item_gui.submitted.connect(self.seq_results)

    def seq_results(self, value):
        self.seq_name = value[0]
        self.sequence = self.project.get_sequence(self.seq_name)
        element = self.sequence.get_element(Asset.HDA)

        fx_list = next(os.walk(element._filepath))[1]
        for name in fx_list:
            if name == "cache":
                fx_list.remove(name)
        fx_list.sort(key=unicode.lower)

        self.item_gui = sfl.SelectFromList(l=fx_list, parent=hou.ui.mainQtWindow(), title="Select an effect to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        name = value[0]
        element = self.sequence.get_element(os.path.join(Asset.HDA, name))


        if element.get_last_version() < 0:
            qd.error("Nothing has been published for this effect")
            return
        filepath = element.get_last_publish()[3]


        try:
            hou.hda.uninstallFile(filepath)
            hou.hda.installFile(filepath)
            #print("no problem here")
        except Exception as e:
            print(e)
            return

        try:
            hda = hou.node("/obj").createNode(name)
        except Exception as e:
            qd.error("Couldn't create node of type " + name + ". You should still be able to tab in the node manually.")

        try:
            hda.setName(name, 1)
        except:
            pass

        try:
            hda.allowEditOfContents()
        except:
            pass