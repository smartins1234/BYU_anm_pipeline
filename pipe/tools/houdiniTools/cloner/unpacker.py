from pxr import Usd, UsdShade, Sdf
#from parser import Parser
import os, hou
from parser import *

class Unpacker:

    def __init__(self):
        print("starting unpacker...")
        self.obj = hou.node("/obj")
        self.layout = self.obj.createNode("subnet")
        self.layout.setName("layout", 1)

    def unpack(self):
        myParser = Parser()
        stage = myParser.parse("/groups/cenote/BYU_anm_pipeline/production/layouts/xochimilco/layout/xochimilco_ref.usda")
        #stage.printAll()
        stage.printStructure()
        atts = []
        for p in stage.prims:
            self.traverse(p, atts)
        '''if prim.getTypeName() == "Mesh":
            parent = prim.getParent()
            for prop in parent.properties:
                if prop.getName() == "reference":
                    path = prop.getValue()
                    geo = self.layout.createNode("geo")
                    geo.setName(parent.getName(), 1)
                    im = geo.createNode("usdimport")
                    im.setName(parent.getName()+"_import", 1)
                    im.parm("filepath1").set(path)
                    im.parm("unpack_geomtype").set(1)'''

    def traverse(self, prim, atts):
        print(prim.getTypeName()+ " " +prim.getName())
        '''for p in prim.prims:
            print("\t"+p.getName()+ " " +p.getTypeName())'''

        if prim.getTypeName() == "Mesh":
            
            parent = prim.getParent()
            if parent is None:
                print("errr, what?")
                return
            for prop in parent.properties:
                if prop.getName() == "reference":
                    path = prop.getValue()
                    geo = self.layout.createNode("geo")
                    geo.setName(parent.getName(), 1)
                    im = geo.createNode("usdimport")
                    im.setName(parent.getName()+"_import", 1)
                    im.parm("filepath1").set(path)
                    im.parm("unpack_geomtype").set(1)
                    prev = im

                    for a in atts:
                        edit = a.getValue()
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
                        print(vex)
                        vex += ";\n@P = @P * trans;"

                        wrangle = geo.createNode("attribwrangle")
                        wrangle.parm("snippet").set(vex)
                        wrangle.setInput(0, prev)
                        wrangle.setDisplayFlag(True)
                        wrangle.setRenderFlag(True)

                        prev = wrangle

                    for att in parent.attributes:
                        if att.getType() == "rel":
                            mat = att.getValue()
                            mat = os.path.basename(str(mat))
                            geo.parm("shop_materialpath").set("/mat/" + mat)

                            return

        elif prim.getTypeName() == "Material":
            pass

        else:
            for a in prim.attributes:
                if a.getType() == "matrix4d":
                    atts.append(a)

            for a in prim.attributes:
                print("\t"+a.getType())
                if a.getType() == "variantset":
                    for v in a.value:                        
                        self.traverse(v, atts)

            for p in prim.prims:
                self.traverse(p, atts)

        #if a mesh, go up a prim and create the reference and apply the transforms, then return
        #else if material:
        #load the material somehow idk :)
        #else:
        #add transforms from this prim, if any, go to the next