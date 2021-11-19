import hou, os
from pxr import Usd, UsdShade, Sdf, Gf
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.select_from_list as sfl
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body, Asset
from pipe.pipeHandlers.element import Element

class AnimCloner:
    def __init__(self):
        self.project = Project()

    def clone(self):
        shot_list = self.project.list_existing_shots()

        self.item_gui = sfl.SelectFromList(l=shot_list, parent=hou.ui.mainQtWindow(), title="Select a shot to clone from")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        self.shot_name = value[0]
        self.shot = self.project.get_shot(self.shot_name)
        element = self.shot.get_element(Asset.ANIMATION)

        asset_list = next(os.walk(element._filepath))[1]
        for name in asset_list:
            if name == "cache":
                asset_list.remove(name)
        asset_list.sort(key=unicode.lower)

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to clone")
        self.item_gui.submitted.connect(self.asset_results)

    def asset_results(self, value):
        self.asset_name = value[0]
        element = self.shot.get_element(os.path.join(Asset.ANIMATION, self.asset_name))

        if element.get_last_version < 0:
            qd.error("There are no publishes for this asset in this shot.")
            return
        path = element.get_last_publish()[3]
        self.build_network(path)

    def build_network(self, path):
        animNode = hou.node("/obj").createNode("cenoteAnimation")
        animNode.setName(self.asset_name + "_anim", 1)
        animNode.parm("fileName").set(path)
        animNode.parm("scale").set(0.01)
        animNode.parm("rendersubd").set(True)

        matPath = self.getMatPath()
        ref = hou.node("/stage").createNode("reference")
        ref.parm("filepath1").set(matPath)
        prim = ref.stage()
        matPrim = None
        for p in prim.Traverse():
            if p.GetTypeName() == "Material":
                #print()
                oldMat = hou.node("/mat/"+self.asset_name)
                if oldMat:
                    oldMat.destroy()

                matNode = hou.node("/mat").createNode("subnet")
                matNode.setName(self.asset_name, 1)
                matName = matNode.name()
                matNode.setMaterialFlag(True)

                animNode.parm("shop_materialpath").set("/mat/"+matName)

                self.buildMaterial(p, matNode)
        
        '''stage = hou.node("/stage")
        subnet = stage.createNode("subnet")
        subnet.setName(self.asset_name, 1)

        sopnet = subnet.createNode("sopnet")
        netName = self.asset_name + "_anim"
        sopnet.setName(netName, 1)
        abc = sopnet.createNode("alembic")

        abc.parm("fileName").set(path)
        abc.parm("loadmode").set(1)
        abc.parm("polysoup").set(0)
        abc.parm("curveFilter").set(0)
        abc.parm("NURBSFilter").set(0)

        sopimport = subnet.createNode("sopimport")
        sopimport.parm("soppath").set(sopnet.path())
        sopimport.setDisplayFlag(True)
        sopimport.parm("asreference").set(1)
        sopimport.parm("primpath").set("/anim/" + self.asset_name)'''

        '''
        #now get and attach materials, no idea if any of this works, btw. I'll have to test it when there's some animations done
        matPath = self.getMatPath()
        lib = subnet.createNode("reference")
        lib.parm("filepath1").set(matPath)
        lib.parm("primpath").set("/anim/" + self.asset_name)
        assign = subnet.createNode("assignmaterial")
        assign.parm("primpattern1").set("/anim/" + self.asset_name)
        assign.parm("matspecpath1").set("/anim/" + self.asset_name + "/" + self.asset_name)
        
        sopimport.setInput(0, subnet.indirectInputs()[0])
        assign.setDisplayFlag(True)
        lib.setInput(0, sopimport)
        assign.setInput(0, lib)

        output = None
        for child in subnet.children():
            if child.name() == "output0":
                output = child
                break
        output.setInput(0, assign)
        output.setDisplayFlag(True)

        subnet.layoutChildren()'''

    def getMatPath(self):
        asset = self.project.get_asset(self.asset_name)
        element = asset.get_element(Asset.MATERIALS)
        if element.get_last_version() < 0:
            return os.path.join(element._filepath, self.asset_name + "_main.usda")
        path = element.get_last_publish()[3]
        return path

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