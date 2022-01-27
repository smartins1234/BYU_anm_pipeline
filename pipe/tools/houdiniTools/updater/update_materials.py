import hou, re
from pipe.pipeHandlers.project import Project
import pipe.pipeHandlers.quick_dialogs as qd

'''
updates all materials in the hip file to their
most recent versions
'''
class MatUpdater:
    def __init__(self):
        self.project = Project()

    def updateAll(self):
        obj = hou.node("/obj")
        mat = hou.node("/mat")
        for node in obj.allSubChildren():
            if node.isMaterialManager():
                for material in node.children():
                    self.updateOne(material)

        for node in mat.children():
            self.updateOne(node)

        qd.message("Updated all materials")

    def updateOne(self, mat):
        assetList = self.project.list_assets()
        for asset in assetList:
            asset = re.sub(r'\W+', '', asset)

        typeName = mat.type().name()
        if typeName not in assetList:
            return #not a material from the pipe, move on

        if mat.isLockedHDA():
            mat.allowEditingOfContents()
        mat.matchCurrentDefinition()
        mat.allowEditingOfContents()

        print(mat.name())