import pymel.core as pm
import os
import glob
import re
from PySide2 import QtWidgets

#from pipe.pipeHandlers import *
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.body import Body, AssetType
import pipe.pipeHandlers.quick_dialogs as qd
import pipe.pipeHandlers.pipeline_io as pipeline_io

import maya.cmds as mc


'''
    Set Asset and Department Environment Variables
'''
def setPublishEnvVar(asset_name, department="model"):
    os.environ["DCC_ASSET_NAME"] = asset_name
    os.environ["DCC_DEPARTMENT"] = department

'''
    Function used whenever a more complex gui is called within Maya
'''
def maya_main_window():
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

'''
    check if user has unsaved changes before performing action, and if so, save as new publish
'''
def check_unsaved_changes():
    unsaved_changes = mc.file(q=True, modified=True)

    if unsaved_changes:
        response = qd.yes_or_no("Would you like to publish the current asset before you proceed?", title="Unsaved changes detected", details="(Press No if you just created a new scene or opened Maya.)")
        if response is True:
            # instead of saving, publish.
            scene = mc.file(q=True, sceneName=True)
            dir_path = scene.split("assets/")
            try:
                asset_path = dir_path[1].split("/")
            except:
                # scene path is stored in the user directory instead of assets. We can't get the asset name, so they must publish manually.
                qd.error("Publish failed. Please publish manually before cloning the new asset.")
                return
            asset_name = asset_path[0]
            try:
                department = asset_path[1].split("/")[0]
                print("department " + department)
            except:
                department = None

            if department:
                print("department found")
            else:
                qd.warning("Skipping changes to " + str(asset_name))
                return

            publisher = Publisher(quick_publish=True, export=False)
            publisher.non_gui_publish(asset_name, department)

'''
    Helper function for post_publish()
'''
def get_scene_file():
    filename = pm.system.sceneName()
    if not filename:
        filename = os.environ['HOME']
        filename = os.path.join(filename, 'untitled.mb')
        return filename, True
    else:
        return filename, False

'''
    Helper function for scene_prep()
'''
def clear_construction_history():
    pm.delete(constructionHistory=True, all=True)

'''
    Helper function for scene_prep()
'''
def freeze_transformations():
    failed = []
    objects = pm.ls(transforms=True)
    for scene_object in objects:
        try:
            pm.makeIdentity(scene_object, apply=True)
        except:
            failed.append(scene_object)
    return failed

'''
    Helper function for post_publish()
'''
def convert_to_education():
    print("file info: ", pm.FileInfo().items())
    mc.fileInfo( rm="license")
    print("file info: ", pm.FileInfo().items())
    # pm.FileInfo()['license'] = 'commercial'
    fileName = pm.sceneName()
    pm.saveFile()
    # qd.info('This Maya file has been converted to an education licence')

'''
    Helper function for group_top_level()
'''
def get_top_level_nodes():
    assemblies = pm.ls(assemblies=True)
    pm.select(pm.listCameras(), replace=True)
    cameras = pm.selected()
    pm.select([])
    return [assembly for assembly in assemblies if assembly not in cameras]

'''
    Helper function for scene_prep()
'''
def group_top_level():
    top_level_nodes = get_top_level_nodes()
    print("top level nodes: ", top_level_nodes)
    # If the top level has more than one node, group it.
    # Also, if there's only one top level, and it's not a group, group it.

    if len(top_level_nodes) > 1:
        pm.group(top_level_nodes)
    elif len(top_level_nodes) == 1:
        node = top_level_nodes[0]
        shapes = node.listRelatives(shapes=True)
        if shapes and "group" not in str(node):
            pm.group(top_level_nodes)

'''
    Helper function for scene_prep()
'''
def delete_image_planes():
    objects = pm.ls()
    for scene_object in objects:
        if isinstance(scene_object, pm.nodetypes.ImagePlane):
            pm.delete(scene_object)

'''
    Helper for JSONExporter and AlembicExporter
'''
def get_loaded_references():
    references = pm.ls(references=True)  #, transforms=True)
    loaded=[]

    for ref in references:
        print("Checking status of " + ref)
        try:
            if ref.isLoaded():
                loaded.append(ref)
        except:
            print("Warning: " + ref + " was not associated with a reference file")

    print("loaded: ", loaded)
    return loaded

'''
    Helper for Unloading References
'''
def unload_reference(ref):
    path = ref.fileName(False, True, False)
    mc.file(path, rr=True)

'''
    Helper for JSONExporter
'''
def ref_path_to_ref_name(path):
    pathItems = str(path).split("/")

    for i in range(len(pathItems)):
        if pathItems[i - 1] == "assets":
            return pathItems[i]

'''
    Helper for get_body_from_reference()
'''
def extract_reference_data(ref):
    refPath = pm.referenceQuery(str(ref), filename=True)
    refName = ref_path_to_ref_name(refPath)
    start = refPath.find('{')
    end = refPath.find('}')

    if start == -1 or end == -1:
        vernum = ''
    else:
        vernum = refPath[start+1:end]

    return refName, vernum

'''
    Helper for JSONExporter
'''
def strip_reference(input):
    #TODO:Is there a way for this to selectively avoid props?
    # i = input.rfind(":")  # commenting out because find may cause problems, if not, then we are keeping it.
    return input.split('|')[-1].split(':')[-1]

'''
    Helper for JSONExporter
'''
def find_first_mesh(rootNode):
    print("root: ", str(rootNode))
    firstMesh = None
    path = ""
    stack = []
    stack.append(rootNode)
    while len(stack) > 0 and firstMesh is None:
        curr = stack.pop(0)
        print("curr: ", curr)
        path = path + "/" + strip_reference(curr.name())

        for child in curr.getChildren():
            if isinstance(child, pm.nodetypes.Shape):
                firstMesh = child
                path = path + "/" + strip_reference(child.name())
                break
            elif not isinstance(child, pm.nodetypes.Transform):
                continue
            if child.getShape() is not None: #is_acceptable_anchor(child.getShape()):
                firstMesh = child.getShape()
                path = path + "/" + strip_reference(child.name()) + "/" + strip_reference(child.getShape().name())
                break
        for child in curr.getChildren():
            stack.append(child)

    # import pdb; pdb.set_trace()

    print("firstmesh, path: ", firstMesh, path)

    return firstMesh, path

def is_acceptable_anchor(possibleMesh):
    return (
        possibleMesh
        and isinstance(possibleMesh, pm.nodetypes.Mesh)
        and not possibleMesh.isIntermediateObject()
        and len(possibleMesh.vtx) > 2)


'''
    Helper for JSONExporter
'''
def get_anchor_points(mesh):
    verts = mesh.vtx

    vertpos1 = verts[0].getPosition(space='world')
    vertpos2 = verts[1].getPosition(space='world')
    vertpos3 = verts[2].getPosition(space='world')

    return vertpos1, vertpos2, vertpos3

'''
    Helper for JSONExporter
'''
def get_body_from_reference(ref):
    try:
        body = Project().get_body(extract_reference_data(ref)[0])
        return body
    except:
        print(str(ref) + " is not a body")

    return None

'''
    Helper for JSONExporter and AlembicExporter
'''
def get_root_node_from_reference(ref):
    refPath = pm.referenceQuery(str(ref), filename=True)
    refNodes = pm.referenceQuery(str(refPath), nodes=True )
    rootNode = pm.ls(refNodes[0])[0]
    return rootNode

'''
    Helper for JSONExporter
'''
def has_parent_set(rootNode):
    project = Project()
    parent_is_set = False
    parent_node = rootNode.getParent()

    while parent_node is not None:
        print("parent node: ", parent_node)
        parent_body = get_body_from_reference(parent_node)
        print("parent body: ", parent_body)

        if parent_body is not None and parent_body.is_asset() and parent_body.get_type() == AssetType.SET:
            parent_is_set = True
            break

        try:
            parent_node = parent_node.parent_node()
        except:
            print(str(parent_node) + " is top level")
            parent_node = None

    if parent_is_set:
        return True

    return False

'''
    Helpers for Tagging nodes with flags
'''

def tag_node_with_flag(node, flag):
    if not node_is_tagged_with_flag(node, flag):
        pm.cmds.lockNode(str(node), l=False)
        node.addAttr(flag, dv=True, at=bool, h=False, k=True)

def untag_node_with_flag(node, flag):
    if node_is_tagged_with_flag(node, flag):
        node.deleteAttr(flag)

def node_is_tagged_with_flag(node, flag):
    if node.hasAttr(flag):
        return True

def children_tagged_with_flag(node, flag):
    try:
        for child in node.listRelatives(ad=True):
            # print("child: ", child)
            if node_is_tagged_with_flag(child, flag):
                return True
        return False
    except:
        return False

def get_first_child_with_flag(node, flag):
    stack = []
    stack.append(node)
    while len(stack) > 0:
        curr = stack.pop()
        for child in curr.getChildren():
            if node_is_tagged_with_flag(child, flag):
                return child
        for child in curr.getChildren():
            stack.append(child)

'''
    Save the scene file. Called from education.py shelf tool.
'''
def save_scene_file():
    filename, untitled = get_scene_file()
    if untitled:
        pm.system.renameFile(filename)
    return pm.system.saveFile()

'''
    Resets the transfrom of the object to be at (0,0,0)
'''
def center_object_at_origin():
    print("Centering prop at origin...")
    #select object
    nodes = mc.ls(assemblies=True)
    nodes = remove_cameras(nodes)
    for i in range(0, len(nodes)):

        select = mc.select(nodes[i])

        #get local space pivot
        pivot = mc.xform(query=True, scalePivot=True, worldSpace=False)

        #save that pivot as a custom attribute in case we need it later
        mc.addAttr(longName='oldPos', attributeType='double3')
        mc.addAttr(longName='oldPosX', attributeType='double', parent='oldPos')
        mc.addAttr(longName='oldPosY', attributeType='double', parent='oldPos')
        mc.addAttr(longName='oldPosZ', attributeType='double', parent='oldPos')
        mc.setAttr(str(nodes[i]) + '.oldPos',pivot[0],pivot[1],pivot[2])

        #apply the opposite of that to transform
        transform = mc.xform(t=[-pivot[0],-pivot[1],-pivot[2]])

        #freeze transofrmations
        mc.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

def reposition_object_to_old_pos():
    print("Repositioning object to its old position")
    #select object
    nodes = mc.ls(assemblies=True)
    nodes.remove("persp")
    nodes.remove("top")
    nodes.remove("front")
    nodes.remove("side")
    for i in range(0, len(nodes)):

        select = mc.select(nodes[i])

        #get oldPos attribute OR if it doesn't exist don't transform it
        try:
            x = mc.getAttr(str(nodes[i]) + '.oldPosX')
            y = mc.getAttr(str(nodes[i]) + '.oldPosY')
            z = mc.getAttr(str(nodes[i]) + '.oldPosZ')
            result = mc.xform(t=[x,y,z])
            #mc.deleteAttr(str(nodes[i]) + '.oldPos')
            print("successfully moved " + str(nodes[i]))
        except:
            print("Exception occurred while moving object")



def remove_cameras(list):
        list.remove("persp")
        list.remove("top")
        list.remove("front")
        list.remove("side")
        return list
