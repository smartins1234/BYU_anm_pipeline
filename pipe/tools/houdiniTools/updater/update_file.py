from pipe.tools.houdiniTools.updater.update_layout import LayoutUpdater
from pipe.tools.houdiniTools.updater.update_materials import MatUpdater

class FileUpdater:
    def __init__(self):
        pass

    def update(self):
        layout = LayoutUpdater()
        mat = MatUpdater()

        layout.updateAll()
        mat.updateAll()