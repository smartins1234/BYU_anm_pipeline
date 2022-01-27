import maya.cmds as cmds

'''
Creates a nurbs circle around the selected object to be used
as a control by animators.
'''
class AutoControl:
    def __init__(self):
        pass
    def go(self):
        list = cmds.ls( selection=True, dag=1 )
        max = -1
        for obj in list:
            #print(obj)
            vtx = cmds.ls(obj+'.vtx[*]', fl=True)
            for v in vtx:
                pos = cmds.xform(v, q=True, objectSpace=True, t=True)
                x = pos[0]
                z = pos[2]
                dist = ((x*x) + (z*z)) ** (.5)
                #print(dist)
                if(dist > max):
                    max = dist
        #print(max)
        max = max * 1.3
        circ = cmds.circle( c=(0, 0, 0), nr=(0, 1, 0), r=max )

        cmds.parentConstraint(circ, list[0], mo=True)
        cmds.scaleConstraint(circ, list[0])

        for obj in list:
            try:
                cmds.setAttr(obj+".translateX", lock=True)
                cmds.setAttr(obj+".translateY", lock=True)
                cmds.setAttr(obj+".translateZ", lock=True)
                cmds.setAttr(obj+".rotateX", lock=True)
                cmds.setAttr(obj+".rotateY", lock=True)
                cmds.setAttr(obj+".rotateZ", lock=True)
                cmds.setAttr(obj+".scaleX", lock=True)
                cmds.setAttr(obj+".scaleY", lock=True)
                cmds.setAttr(obj+".scaleZ", lock=True)
            except:
                pass

        cmds.group(list[0], circ, n=list[0]+"_rig")
