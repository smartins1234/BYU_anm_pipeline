'''
this script was given to me by the rigging team to be added to their shelf
'''

# uncompyle6 version 3.5.0
# Python bytecode 2.6 (62161)
# Decompiled from: Python 2.7.5 (default, Aug  7 2019, 00:51:29) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]
# Embedded file name: C:/Users/lee.dunham/Documents/maya/2012-x64/scripts\ld_mirrorMe.py
# Compiled at: 2012-05-21 16:29:56
"""
| Script:     | ld_mirrorMe.py
| Version:    | 1.5.0
| Licence:    | Creative Commons, Attribution, Share Alike
| Authors:    | Copyright 2012 Lee Dunham
| Contact:    | leedunham@gmail.com - www.ldunham.blogspot.com
| Usage:      | import ld_mirrorMe
|             | ld_mirrorMe.GUI()
|             |
| Required:   | maya.cmds
|             | maya.mel
|             | ld_mirrorMe
| Desc:       | Quickly mirror various objects, nurbs-curves, geo and deformers to speed up workflow.
| Updates:
              09/03/2012 - 0.5.0
              Initial working version.
              
              10/03/12 - 0.9.5
              Tidied UI and reduced/cleaned code.
              
              13/03/12 - 1.0.0
              Added colour option for curves.
              Removed all pymel (speed issues).
              Allowed multi-mirroring.
              
              14/03/12 - 1.5.0
              Thanks to Matt Murray for feedback for further improvements.
              Added option to mirror world position of mirrored curve.
              Added further error-checking for all modes.
              Fixed bug causing unwanted locking of attributes.
              Added option to disable colouring of mirrored curve.
"""
import maya.cmds as mc, maya.mel as mm

def GUI():
    winName = 'ld_mirrorMe_win'
    if mc.window(winName, ex=1):
        mc.deleteUI(winName)
    mc.window(winName, t='ld_mirrorMe', s=0)
    mc.columnLayout(adj=1)
    mc.frameLayout(l='MirrorMe', cll=0)
    mc.columnLayout(adj=1)
    mc.radioButtonGrp('ld_mirrorMode_rBGrp', l=' Mode:', la3=['Curve', 'Mesh', 'Deformer'], nrb=3, cw4=[50, 60, 60, 60], cal=[1, 'left'], sl=1, cc=lambda *args: switchMode())
    mc.radioButtonGrp('ld_mirrorAxis_rBGrp', l=' Axis:', la3=['X', 'Y', 'Z'], nrb=3, cw4=[50, 60, 60, 60], cal=[1, 'left'], sl=1)
    mc.rowColumnLayout(nc=2, cw=[1, 50])
    mc.text(l='Search:')
    mc.textField('ld_mm_search_tField', tx='L_', w=175)
    mc.text(l='Replace:')
    mc.textField('ld_mm_replace_tField', tx='R_', w=175)
    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout('ld_mMode1_fLayout', l='Curve', cll=0)
    mc.columnLayout(adj=1)
    mc.radioButtonGrp('ld_mCurve_position_rBGrp', l=' Position:', la3=['World 0', 'Original', 'Mirrored'], nrb=3, cw4=[50, 60, 60, 60], cal=[1, 'left'], sl=1)
    mc.rowLayout(nc=2, adj=1)
    mc.colorIndexSliderGrp('ld_mCurve_colour_cISGrp', l='Colour:', cal=[1, 'center'], h=20, cw3=[35, 30, 90], min=1, max=32, v=7)
    mc.checkBox('ld_mCurve_colour_cBox', l='', w=15, v=1, onc='mc.colorIndexSliderGrp("ld_mCurve_colour_cISGrp",e=1,en=1)', ofc='mc.colorIndexSliderGrp("ld_mCurve_colour_cISGrp",e=1,en=0)')
    mc.setParent('..')
    mc.rowColumnLayout(nc=2, cw=[1, 70])
    mc.button(l='Curve(s)', c=lambda *args: addToField('ld_mCurve_original_tField', 1))
    mc.textField('ld_mCurve_original_tField', w=175)
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout('ld_mMode2_fLayout', l='Mesh', cll=0, m=0)
    mc.columnLayout(adj=1)
    mc.radioButtonGrp('ld_mMesh_position_rBGrp', l=' Position:', la2=['Target', 'Original'], nrb=2, cw3=[50, 90, 90], cal=[1, 'left'], sl=1)
    mc.rowColumnLayout(nc=2, cw=[1, 70])
    mc.button(l='Original', c=lambda *args: addToField('ld_mMesh_original_tField', 0))
    mc.textField('ld_mMesh_original_tField', w=175)
    mc.button(l='Target(s)', c=lambda *args: addToField('ld_mMesh_target_tField', 1))
    mc.textField('ld_mMesh_target_tField', w=175)
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.frameLayout('ld_mMode3_fLayout', l='Deformer', cll=0, m=0)
    mc.columnLayout(adj=1)
    mc.text(l='(This version only supports Cluster deformers)\n')
    mc.rowColumnLayout(nc=2, cw=[1, 70])
    mc.button(l='Object', c=lambda *args: addToField('ld_mDeformer_object_tField', 0))
    mc.textField('ld_mDeformer_object_tField', w=175)
    mc.button(l='Deformer(s)', c=lambda *args: addToField('ld_mDeformer_deformer_tField', 1))
    mc.textField('ld_mDeformer_deformer_tField', w=175)
    mc.setParent('..')
    mc.setParent('..')
    mc.setParent('..')
    mc.button(l='Mirror!', h=35, c=lambda *args: mirrorMeCmd(mc.radioButtonGrp('ld_mirrorMode_rBGrp', q=1, sl=1)))
    mc.setParent('..')
    mc.text(al='right', h=15, bgc=(0.4, 0.3, 0.3), fn='smallBoldLabelFont', l='%s ldunham.blogspot.com' % u'\xa9')
    mc.showWindow(winName)


def switchLayouts(mode):
    allModes = [
     1, 2, 3]
    allModes.remove(mode)
    for m in allModes:
        mc.frameLayout('ld_mMode%s_fLayout' % m, e=1, m=0)

    mc.frameLayout('ld_mMode%s_fLayout' % mode, e=1, m=1)


def switchMode():
    switchLayouts(mc.radioButtonGrp('ld_mirrorMode_rBGrp', q=1, sl=1))


def addToField(fieldName, multi):
    objects = mc.ls(sl=1)
    data = ''
    if len(objects) == 0:
        return
    if multi == 0:
        data = objects[0]
    elif multi == 1:
        data = (', ').join(objects)
    mc.textField(fieldName, e=1, tx=data)


def invertValue(values, index):
    values[(index - 1)] *= -1
    return values


def repositionDeformer(deformerHandle, position):
    mc.xform(deformerHandle, a=1, ws=1, piv=(position[0], position[1], position[2]))
    deformerShape = mc.listRelatives(deformerHandle, c=1, s=1)
    mc.setAttr(deformerShape[0] + '.origin', position[0], position[1], position[2])


def getInfoDeformer(deformerHandle):
    results = []
    cDeformer = mc.listConnections(deformerHandle + '.worldMatrix[0]', type='cluster', d=1)
    cSet = mc.listConnections(cDeformer[0], type='objectSet')
    components = mc.filterExpand(mc.sets(cSet[0], q=1), sm=(28, 31, 36, 46))
    for vertex in components:
        vert = [
         vertex]
        vertWeight = mc.percent(cDeformer[0], vertex, q=1, v=1)
        vert.append(vertWeight[0])
        results.append(vert)

    return results


def filterDeformer(object, deformerHandle):
    results = []
    returned = getInfoDeformer(deformerHandle)
    for vert in returned:
        name = vert[0]
        if name.startswith(object):
            results.append(vert)

    return results


def mirrorMeCmd(mode):
    axis = mc.radioButtonGrp('ld_mirrorAxis_rBGrp', q=True, sl=True)
    search = mc.textField('ld_mm_search_tField', q=True, tx=True)
    replace = mc.textField('ld_mm_replace_tField', q=True, tx=True)
    if mode == 1:
        pre_shapeMirror(mc.textField('ld_mCurve_original_tField', q=True, tx=True), axis, mc.radioButtonGrp('ld_mCurve_position_rBGrp', q=True, sl=True), search, replace)
    elif mode == 2:
        pre_meshMirror(mc.textField('ld_mMesh_original_tField', q=True, tx=True), mc.textField('ld_mMesh_target_tField', q=True, tx=True), axis, mc.radioButtonGrp('ld_mMesh_position_rBGrp', q=True, sl=True), search, replace)
    elif mode == 3:
        pre_deformerMirror(mc.textField('ld_mDeformer_object_tField', q=True, tx=True), mc.textField('ld_mDeformer_deformer_tField', q=True, tx=True), axis, search, replace)


def pre_shapeMirror(original, axis, position, search, replace):
    listTarget = original.split(', ')
    if len(original) == 0:
        return
    for obj in listTarget:
        shapeMirror(obj, axis, position, search, replace)


def shapeMirror(original, axis, position, search, replace):
    if not mc.objectType(mc.listRelatives(original, c=1, s=1)[0], isType='nurbsCurve'):
        return
    else:
        origPos = mc.xform(original, q=1, ws=1, rp=1)
        origRot = mc.xform(original, q=1, ws=1, ro=1)
        mc.move(0, 0, 0, original, ws=1)
        mc.rotate(0, 0, 0, original, ws=1)
        curveTarget = mc.duplicate(original, rr=1)
        for i in range(mc.getAttr(original + '.spans') + mc.getAttr(original + '.degree')):
            pos = invertValue(mc.xform(original + '.cv[%s]' % i, q=1, ws=1, t=1), axis)
            mc.move(pos[0], pos[1], pos[2], curveTarget[0] + '.cv[%s]' % i, ws=1)

        mc.move(origPos[0], origPos[1], origPos[2], original, ws=1)
        mc.rotate(origRot[0], origRot[1], origRot[2], original, ws=1)
        if mc.listRelatives(original, p=1) != None:
            mc.parent(curveTarget[0], w=1)
        if position == 2:
            mc.move(origPos[0], origPos[1], origPos[2], curveTarget[0], ws=1)
            mc.rotate(origRot[0], origRot[1], origRot[2], curveTarget[0], ws=1)
        elif position == 3:
            mirroredPos = invertValue(origPos, axis)
            mc.move(mirroredPos[0], mirroredPos[1], mirroredPos[2], curveTarget[0], ws=1)
        if mc.checkBox('ld_mCurve_colour_cBox', q=1, v=1) == 1:
            colourObject = curveTarget[0] + '.overrideColor'
            if mc.getAttr(mc.listRelatives(original, c=1, s=1)[0] + '.overrideEnabled') == 1:
                colourObject = mc.listRelatives(curveTarget[0], c=1, s=1)[0] + '.overrideColor'
            mc.setAttr(colourObject, mc.colorIndexSliderGrp('ld_mCurve_colour_cISGrp', q=1, v=1) - 1)
        mc.rename(curveTarget[0], original.replace(search, replace))
        return


def pre_meshMirror(original, target, axis, position, search, replace):
    listTarget = target.split(', ')
    if len(original) == 0 or len(target) == 0:
        return
    type = mc.objectType(mc.listRelatives(original, c=1, s=1)[0])
    origCompCount = 0
    if type == 'mesh':
        origCompCount = mc.polyEvaluate(original, v=1)
    elif type == 'nurbsSurface':
        origShape = mc.listRelatives(original, c=1, s=1)
        origCompCount = mc.getAttr(origShape[0] + '.spansU') + mc.getAttr(origShape[0] + '.spansV')
    for obj in listTarget:
        meshMirror(original, obj, type, origCompCount, axis, position, search, replace)


def meshMirror(original, target, type, origCompCount, axis, position, search, replace):
    targetCount = 0
    if type == 'mesh':
        try:
            targetCount = mc.polyEvaluate(target, v=1)
        except:
            mc.warning('%s does not match %s. Skipped' % (target, original))
            return

    elif type == 'nurbsSurface':
        try:
            targetShape = mc.listRelatives(target, c=1, s=1)
            targetCount = mc.getAttr(targetShape[0] + '.spansU') + mc.getAttr(targetShape[0] + '.spansV')
        except:
            mc.warning('%s does not match %s. Skipped' % (target, original))
            return

    if targetCount != origCompCount:
        mc.warning('%s does not match %s. Skipped' % (target, original))
        return
    attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    attrListLock = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for a in range(len(attrList)):
        attrListLock[a] = int(mc.getAttr(original + '.' + attrList[a], lock=1))
        mc.setAttr(original + '.' + attrList[a], lock=0)

    mirrorObj = target + 'suffTemp'
    scaleObj = mc.duplicate(original, rr=1)[0]
    mc.duplicate(original, rr=1, n='tempName')
    mc.rename('tempName', mirrorObj)
    for i in (attr for attr in range(len(attrList)) if attrListLock[attr]):
        mc.setAttr(original + '.' + attrList[i], lock=1)

    mc.setAttr(scaleObj + '.' + attrList[(axis + 5)], -1 * float(mc.getAttr(scaleObj + '.' + attrList[(axis + 5)])))
    blendshape = mc.blendShape(target, scaleObj, frontOfChain=1)
    mc.select(mirrorObj, scaleObj, r=1)
    mm.eval('doWrapArgList "6" {"1","0","1","2","1","1","0"};')
    mc.setAttr('wrap1.exclusiveBind', 1)
    mc.setAttr(blendshape[0] + '.' + target, 1)
    mc.select(mirrorObj, r=1)
    mc.DeleteHistory
    mc.delete(ch=1)
    mc.delete(scaleObj + 'Base', scaleObj)
    if position == 1:
        mc.setAttr(mirrorObj + '.tx', float(mc.getAttr(target + '.tx')))
        mc.setAttr(mirrorObj + '.ty', float(mc.getAttr(target + '.ty')))
        mc.setAttr(mirrorObj + '.tz', float(mc.getAttr(target + '.tz')))
    mirror = mirrorObj.replace(search, replace).replace('suffTemp', '')
    mc.rename(mirrorObj, mirror)


def pre_deformerMirror(object, deformers, axis, search, replace):
    listDeformers = deformers.split(', ')
    if len(object) == 0 or len(deformers) == 0:
        return
    for deformerHandle in listDeformers:
        deformerMirror(object, deformerHandle, axis, search, replace)


def deformerMirror(object, deformerHandle, axis, search, replace):
    if not mc.objectType(mc.listRelatives(deformerHandle, c=1, s=1)[0], isType='clusterHandle'):
        mc.warning('Current version only supports cluster deformers')
        return
    shapes = mc.listRelatives(object, s=1, c=1)
    oldList = filterDeformer(object, deformerHandle)
    for pair in oldList:
        pointPos = mc.pointPosition(pair[0], l=1)
        node = mc.createNode('closestPointOnMesh')
        mc.setAttr(('%s.inPosition' % node), *invertValue(pointPos, axis))
        try:
            mc.connectAttr('%s.outMesh' % shapes[0], '%s.inMesh' % node, f=1)
        except:
            pass
        else:
            pair[0] = '%s.vtx[%s]' % (object, mc.getAttr('%s.closestVertexIndex' % node))
            mc.delete(node)

    amount = len(oldList)
    newPoints = [ oldList[x][0] for x in range(amount) ]
    clusDeformer = mc.listConnections('%s.worldMatrix[0]' % deformerHandle, type='cluster', d=1)
    newClus = mc.cluster(newPoints, rel=mc.getAttr('%s.relative' % clusDeformer[0]))
    for x in range(amount):
        mc.percent(newClus[0], oldList[x][0], v=oldList[x][1])

    aPos = mc.xform(object, q=1, ws=1, rp=1)
    pos = bPos = mc.xform(deformerHandle, q=1, ws=1, rp=1)
    pos[axis - 1] = bPos[(axis - 1)] - (bPos[(axis - 1)] - aPos[(axis - 1)]) * 2
    mc.xform(newClus, a=1, ws=1, piv=(pos[0], pos[1], pos[2]))
    mc.setAttr(mc.listRelatives(newClus, c=1, s=1)[0] + '.origin', pos[0], pos[1], pos[2])
    mc.rename(newClus[1], deformerHandle.replace(search, replace))

class MirrorClusters():
    def __init__(self):
        pass

    def run(self):
        GUI()