from pxr import Usd, UsdShade, Sdf
import os, hou

class Unpacker:

    def __init__(self):
        print("starting unpacker...")

    def unpack_usd(self, file):

        '''THIS IS TEMPORARY, REMOVE ONCE THE TOOL IS COMPLETE
        for node in hou.node("/obj").children():
            node.destroy()
        for node in hou.node("/mat").children():
            node.destroy()
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

        node = hou.node("/stage").createNode("reference")
        node.parm("filepath1").set(file)

        #node = hou.selectedNodes()[0]
        stage = node.stage()

        prims = stage.Traverse()                            
                                
        for p in prims: 
            path = p.GetAttribute("ref_path")
            if path:
                print(p.GetName() + " is referenced and is a " + p.GetTypeName())
                
                if p.GetTypeName() == "Xform":
                    self.build_geo(p, path)
            
            path = p.GetAttribute("hda_path")
            if path:    #we're going to assume this is a material
                print("Loading material " + p.GetName())
                mat = hou.node("/mat")
                hou.hda.installFile(path.Get())
                definition = hou.hda.definitionsInFile(path.Get())[0]
                nodeType = definition.nodeTypeName()

                newMat = mat.createNode(nodeType, p.GetName())
                newMat.setColor(hou.Color((01.0,1.0,0.2)))
                    
        node.destroy()

    '''def create_materials(self, prims):
        mat = hou.node("/mat")
        for p in prims:
            if p.GetTypeName() == "Material":
                hou.hda.installFile(hda_path)
                definition = hou.hda.definitionsInFile(hda_path)
                nodeType = definition.nodeTypeName()
                
                newMat = mat.createNode(nodeType, p.GetName())
                newMat.setColor(hou.Color((0.2,0.0,0.8)))
            path = p.GetAttribute("ref_path")
            if path and p.GetTypeName != "Xform": #these are materials then
                children = p.GetAllChildren()
                #print(children)
                for child in children:
                    if child.GetTypeName() == "Material":
                        #create material node
                        myMat = mat.createNode("pxrmaterialbuilder", child.GetName())
                        shaders = child.GetAllChildren()
                        self.build_shaders(shaders, myMat)

        mat.layoutChildren()'''
    '''
    def build_shaders(self, shaders, material):
        for shader in shaders:
            if shader.GetAttribute("info:id").Get() != "UsdPreviewSurface":
                node = material.createNode(shader.GetAttribute("info:id").Get().lower(), shader.GetName())
                #print(shader.GetAttributes())
                for att in shader.GetPropertiesInNamespace("inputs"):
                    print(att)


        material.layoutChildren()'''

    def build_geo(self, p, path):
        geo = hou.node("/obj").createNode("geo", p.GetName())
        im = geo.createNode("usdimport", p.GetName())
        imPath = im.parm('filepath1')
        imPath.set(path.Get())
        im.parm("input_unpack").set(1)
        im.parm("unpack_geomtype").set(1)
        
        edit = p.GetAttribute("xformOp:transform:edit").Get()
        vex = "matrix trans = {{"
        for x in range(0, 4):
            for y in range(0, 4):
                vex += str(edit[x][y])
                if y != 3:
                    vex += ","
                else:
                    vex += "}"
            if x != 3:
                vex += ",{"
            else:
                vex += "}"
        #print(vex)
        vex += ";\n@P = @P * trans;"
        
        wrangle = geo.createNode("attribwrangle")
        wrangle.parm("snippet").set(vex)
        wrangle.setInput(0, im)
        wrangle.setDisplayFlag(True)
        wrangle.setRenderFlag(True)
        
        rel = p.GetRelationship("material:binding").GetTargets()[0]
        rel = os.path.basename(str(rel))
        print(rel)
        
        geo.parm("shop_materialpath").set("/mat/" + rel)
        
        geo.layoutChildren()
        hou.node("/obj").layoutChildren()