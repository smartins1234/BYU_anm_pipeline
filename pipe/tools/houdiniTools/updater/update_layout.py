from pxr import Usd, UsdShade, Sdf, Gf
import os, hou, pprint, re, shutil
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
import pipe.pipeHandlers.pipeline_io as pio

class LayoutUpdater:
    def __init__(self):
        self.project = Project()
        self.assetList = self.project.list_assets()
        for asset in self.assetList:
            asset = re.sub(r'\W+', '', asset)

    def updateAll(self):
        obj = hou.node("/obj")
        for node in obj.children():
            if node.type().name() == "cenoteLayoutNet":
                self.updateLayout(node)

    def updateLayout(self, layout):
        print("updating " + layout.name())
        #reload its usd reference node
        self.reloadUsd(layout)
        #update all materials in the layout's library
        lib = None
        for node in layout.children():
            if node.type().name() == "matnet":
                lib = node
        
        matList = []
        for mat in lib.children():
            self.reloadMaterial(mat)
            matList.append(mat.name())

        #undo all material assignments (set to 0)
        layout.parm("num_materials").set(0)
        #parse through the material bindings again
        matDict = self.getMatDict(layout)
        self.assignMats(layout, matDict, matList, lib)
        
        qd.message("Successfully updated " + layout.name())

    def reloadUsd(self, layout):
        refNodePath = layout.parm("loppath").eval()
        refNode = hou.node(refNodePath)
        refNode.parm("reload").pressButton()

    def reloadMaterial(self, matNode):
        typeName = matNode.type().name()
        if typeName not in self.assetList:
            return #not a material from the pipe, move on

        if matNode.isLockedHDA():
            matNode.allowEditingOfContents()
        matNode.matchCurrentDefinition()
        matNode.allowEditingOfContents()

    def getMatDict(self, layout):
        refNodePath = layout.parm("loppath").eval()
        refNode = hou.node(refNodePath)
        stage = refNode.stage()
        matDict = {}

        for prim in stage.Traverse():
            #print(prim.GetName() + " " + prim.GetTypeName())

            mat_path = prim.GetRelationship("material:binding")
            #we decide what to copy into it's own geometry node by what has its own material
            if mat_path:
                #print(prim.GetName() + " has a material at path " + str(mat_path.GetForwardedTargets()[0]))

                primPaths = ""
                if prim.GetTypeName() == "Mesh":
                    primPaths = primPaths + "@path=" + str(prim.GetPath()) + " "
                else:
                    children = self.getDescendants(prim)
                    for child in children:
                        if child.GetTypeName() == "Mesh":
                            primPaths = primPaths + "@path=" + str(child.GetPath()) + " "
                
                mat_path = mat_path.GetForwardedTargets()
                if mat_path[0].IsPrimPath():
                    #print(mat_path[0])
                    mat_name = os.path.basename(str(mat_path[0]))
                    #print("\t" + mat_name)

                    if mat_name in matDict.keys():
                        matDict[mat_name] += primPaths
                    else:
                        matDict[mat_name] = primPaths

        return matDict

    def assignMats(self, layout, matDict, matList, library):

        layout.parm("num_materials").set(len(matDict.keys()))
        index = 1

        for mat in matDict.keys():
            if re.sub(r'\W+', '', mat) in matList:
                #this material is already up to date
                pass
            else:
                #clone in that material's hda to the network
                asset = self.project.get_asset(mat)
                if not asset:
                    print("Well there's your problem :/")
                    continue
                    
                element = asset.get_element(Asset.MATERIALS)
                matNode = None
                if element.get_last_version() >= 0:
                    path = element.get_last_publish()[3]
                    hdaPath = path.split(".")[0] + ".hda"
                    try:
                        hou.hda.installFile(hdaPath)

                        matNode = library.createNode(re.sub(r'\W+', '', mat))
                        matNode.setName(mat, 1)
                        matNode.setMaterialFlag(True)
                    except Exception as e:
                        qd.error("The material for " + mat + " needs to be republished. Sorry for the inconvenience.")
                        #print(e)

                #assign the material to all the paths
                layout.parm("group"+str(index)).set(matDict[mat])
                if matNode:
                    layout.parm("shop_materialpath"+str(index)).set(matNode.path())

            index += 1

    def getDescendants(self, prim):
        all = []
        children = prim.GetChildren()
        all.extend(children)
        for child in children:
            all.extend(self.getDescendants(child))

        return all

#the only part that should need to be redone is the material stuff
#so first, make sure to reload the usda file
#from there, the lop import should be fine, so don't mess with that
#parse through the usda to get the material assignments
#and apply the materials like before

#updating the materials might also be a problem, they won't update automatically but
#there might be a way to force it to update from the hda file, which should take
#care of it.

#for each material node
#check if it's an hda
#check if it's unlocked, if not then unlock it
#call hou.Node.matchCurrentDefinition()
#unlock it again