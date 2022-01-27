import hou

from pipe.tools.houdiniTools.updater.update_layout import LayoutUpdater
from pipe.tools.houdiniTools.updater.update_materials import MatUpdater
import pipe.pipeHandlers.quick_dialogs as qd

'''
updates all layouts and materials in the hip file to
their most recent versions
'''
class FileUpdater:
    def __init__(self):
        pass

    def update(self):
        layout = LayoutUpdater()
        mat = MatUpdater()

        layout.updateAll()
        mat.updateAll()

        for node in hou.node("/obj").children():
            if node.type().name() == "cenoteCamera" or node.type().name() == "cenoteAnimation":
                try:
                    node.parm("buildHierarchy").pressButton()
                except Exception as e:
                    print(e)
                    qd.warning("Couldn't update node " + node.name())
        qd.message("Camera and Animation nodes successfully updated. Remember to check your render node camera paths!")
