'''
changes the display setting of each shape node so only the objects selected will change color
adding color will add it to each shape node of the selected objects
reseting it will put the display options back to the default
'''

import maya.cmds as mc

#UI variables
colorVar = ""
toolCreate = "Shape_Color_Editor"
selectHierarchy = True

                
#button pushed function
def donePush(null):
    mc.deleteUI(toolCreate)
       
def addPush(null):
    global colorVar
    shapeOverride(1, mc.colorIndexSliderGrp(colorVar, q = True, value = True)-1)
    
def resetPush(null):
    shapeOverride(0, 0)

#shape override helper function
def shapeOverride(enableOverride, overrideColor):
    #checking if heiarchy needs to be selected
    if selectHierarchy:
        mc.select(hi = True)
    selectList = mc.ls(sl = True)
    objectsChanged = 0
    print(selectList)
    for currObject in selectList:
        #finding shapes
        if str(mc.nodeType(currObject)) == "transform":
            shapeList = mc.listRelatives(currObject, shapes=True)
            print(shapeList)
            if shapeList != None:
                objectsChanged += 1
                for shape in shapeList:
                    mc.setAttr(currObject + "|" + shape + ".overrideEnabled", enableOverride)
                    mc.setAttr(currObject + "|" + shape + ".overrideColor", overrideColor)
    if objectsChanged == 0:
        mc.warning("no object's color was changed")

def windowCreate():
    global colorVar
    toolName = "Shape Color Editor"
    #delete already created window
    if mc.window(toolCreate, exists=True):
        mc.deleteUI(toolCreate)
    mc.window(toolCreate, t=toolName, widthHeight = (500,500))
    mc.frameLayout(label="color Override")
    #initializing color slider
    colorVar = mc.colorIndexSliderGrp( label="", adj = True, min=1, max=32, value=10)
    #select hierarchy check box
    mc.checkBox(label="select hierarchy", onc = "selectHierarchy = True", ofc = "selectHierarchy = False", value = True)
    #initializing button
    mc.button(label="Reset", command=resetPush)
    mc.button(label="Add Color", command=addPush)
    mc.button(label="Done", command=donePush)
    mc.showWindow(toolCreate)   
windowCreate() 
