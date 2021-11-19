import hou
from pxr import Usd, UsdShade, Sdf, Gf
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class MaterialCloner:

    def __init__(self):
        self.project = Project()

    def clone(self):
        asset_list = self.project.list_existing_assets()

        self.item_gui = sfl.SelectFromList(
            l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset's material to clone")
        self.item_gui.submitted.connect(self.results)

    def results(self, value):
        print("Selected asset: " + value[0])
        filename = value[0]

        self.body = Project().get_body(filename)
        self.element = self.body.get_element(Asset.MATERIALS)
        if self.element.get_last_version() >= 0:

            path = self.element.get_last_publish()[3]
            if path:
                ref = hou.node("/stage").createNode("reference")
                ref.setName(filename+"_material_ref", 1)
                ref.parm("filepath1").set(path)
                ref.parm("primpath").set("/materials/")

                stage = ref.stage()
                for prim in stage.Traverse():
                    if prim.GetTypeName() == "Material":
                        
                        oldMat = hou.node("/mat/"+filename)
                        if oldMat:
                            oldMat.destroy()

                        matNode = hou.node("/mat").createNode("subnet")
                        matNode.setName(filename, 1)
                        matName = matNode.name()
                        matNode.setMaterialFlag(True)

                        self.buildMaterial(prim, matNode)

        else:
            qd.error("Nothing was cloned")

    def buildMaterial(self, prim, node):
        output = node.createNode("collect")
        try:
            for shaderPrim in prim.GetChildren():
                name = shaderPrim.GetName()
                id = shaderPrim.GetProperty("info:id")
                id = id.Get()
                print("\t\t"+id)
                shader = node.createNode(id.lower())
                shader.setName(name)

                props = shaderPrim.GetAuthoredProperties()
                for p in props:
                    val = p.Get()
                    if val and p.GetNamespace() == "inputs":
                        #print("\t\t\t"+str(val))#+"\ttype: "+str(type(val)))
                        if type(val) == Sdf.AssetPath:
                            val = str(val)
                            val = val[1:-1]
                            #print("\t\t\t"+val)

                            shader.parm(p.GetBaseName()).set(val)
                        elif type(val) == Gf.Vec3f and id == "PxrArithmetic":
                            #print("\t\t\t"+str(val[0])+" "+str(val[1])+" "+str(val[2]))
                            temp1 = p.GetBaseName()+"1"
                            temp2 = p.GetBaseName()+"2"
                            temp3 = p.GetBaseName()+"3"

                            shader.parm(temp1).set(val[0])
                            shader.parm(temp2).set(val[1])
                            shader.parm(temp3).set(val[2])
                        elif type(val) == Gf.Vec3f:
                            #print("\t\t\t"+str(val[0])+" "+str(val[1])+" "+str(val[2]))
                            temp1 = p.GetBaseName()+"r"
                            temp2 = p.GetBaseName()+"g"
                            temp3 = p.GetBaseName()+"b"

                            shader.parm(temp1).set(val[0])
                            shader.parm(temp2).set(val[1])
                            shader.parm(temp3).set(val[2])

                        else:
                            shader.parm(p.GetBaseName()).set(val)

            for shaderPrim in prim.GetChildren():
                name = shaderPrim.GetName()
                shaderPrim = UsdShade.ConnectableAPI(shaderPrim)
                ins = shaderPrim.GetInputs()
                for inp in ins:
                    connection = inp.GetRawConnectedSourcePaths()
                    if len(connection) > 0:
                        connection = str(connection[0])
                        #print(connection)
                        info = connection.split("/")[-1]
                        outNode, outParm = info.split(":")
                        outNode = outNode.split(".")[0]

                        inNode = name
                        inParm = inp.GetBaseName()

                        #print(outNode, outParm, inNode, inParm)
                        outNode = hou.node("/mat/"+node.name()+"/"+outNode)
                        inNode = hou.node("/mat/"+node.name()+"/"+inNode)
                        inNode.setNamedInput(inParm, outNode, outParm)

        except Exception as e:
            print(e)
            return

        shaderApiPrim = UsdShade.ConnectableAPI(prim)
        outs = shaderApiPrim.GetOutputs()
        for out in outs:
            connection = out.GetRawConnectedSourcePaths()
            if len(connection) > 0:
                connection = str(connection[0])

                info = connection.split("/")[-1]
                outNode, outParm = info.split(":")
                outNode = outNode.split(".")[0]

                inNode = output

                outNode = hou.node("/mat/"+node.name()+"/"+outNode)
                inNode.setNextInput(outNode, outNode.outputIndex(outParm))