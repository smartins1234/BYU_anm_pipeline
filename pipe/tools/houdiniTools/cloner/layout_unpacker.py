from pxr import Usd, UsdShade, Sdf, Gf
import os, hou, pprint, re, shutil
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element
import pipe.pipeHandlers.pipeline_io as pio

'''
pulls layouts into the obj context
'''
class LayoutUnpacker:
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

        self.unpack(path)

    def layout_results(self, value):
        self.layout_name = value[0]

        # copy ref file into the shot
        layout_body = self.project.get_layout(self.layout_name)
        element = layout_body.get_element(Asset.LAYOUT)
        src = os.path.join(element._filepath, self.layout_name + "_ref.usda")
        dst = os.path.join(self.layout_element._filepath, self.shot_name + ".usda")
        shutil.copy(src, dst)
        pio.set_permissions(dst)
        self.unpack(dst)

    def unpack(self, file):
        #delete copies of the same layout node for simplicity
        for lopNode in hou.node("/stage").children():
            if lopNode.type().name() == "loadlayer" and lopNode.parm("filepath").eval() == file:
                lopNode.destroy()

        ref = hou.node("/stage").createNode("loadlayer")
        ref.setName("layout_ref", 1)
        ref.parm("filepath").set(file)

        ref.setDisplayFlag(True)

        rop = hou.node("/stage").createNode("usd_rop")
        rop.setInput(0, ref)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
        rop.parm("lopoutput").set(file)
        rop.setName("save_layout", 1)

        obj = hou.node("/obj")
        matContext = hou.node("/mat")

        #layout = obj.createNode("cenoteLayout")
        layout = obj.createNode("cenoteLayoutNet")
        
        layout.setName(self.shot_name + "_layout", 1)
        layout.parm("scale").set(0.01)
        
        stage = ref.stage()

        layout.parm("loppath").set(ref.path())
        layout.parm("primpattern").set("/layout")
        
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
                    print("\t" + mat_name)

                    if mat_name in matDict.keys():
                        matDict[mat_name] += primPaths
                    else:
                        matDict[mat_name] = primPaths

        #pprint.pprint(matDict)
        library = None
        for child in layout.children():
            if child.type().name() == "matnet":
                library = child
        if not library:
            library = layout.createNode("matnet")
        
        layout.parm("num_materials").set(len(matDict.keys()))
        index = 1

        for mat in matDict.keys():
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
                except:
                    qd.error("The material for " + mat + " needs to be republished. Sorry for the inconvenience.")

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