import pymel.core as pm
from shelfBase import _shelf

class modelingShelf(_shelf):
    def build(self):
        gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
        pm.shelfLayout("BYU Modeling", cellWidth=33, cellHeight=33, p=gShelfTopLevel)

        self.addButton(label="test", icon="/users/guest/s/secybyu/Desktop/BYU_anm_pipeline-main/pipe/tools/_resources/1.png")

class riggingShelf(_shelf):
    def build(self):
        gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
        pm.shelfLayout("BYU Rigging", cellWidth=33, cellHeight=33, p=gShelfTopLevel)

        self.addButton(label="test", icon="/users/guest/s/secybyu/Desktop/BYU_anm_pipeline-main/pipe/tools/_resources/1.png")

class animShelf(_shelf):
    def build(self):
        gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
        pm.shelfLayout("BYU Animation", cellWidth=33, cellHeight=33, p=gShelfTopLevel)

        self.addButton(label="test", icon="/users/guest/s/secybyu/Desktop/BYU_anm_pipeline-main/pipe/tools/_resources/1.png")

class previsShelf(_shelf):
    def build(self):
        gShelfTopLevel = pm.mel.eval('global string $gShelfTopLevel; string $temp=$gShelfTopLevel')
        pm.shelfLayout("BYU Previs", cellWidth=33, cellHeight=33, p=gShelfTopLevel)

        self.addButton(label="test", icon="/users/guest/s/secybyu/Desktop/BYU_anm_pipeline-main/pipe/tools/_resources/1.png")