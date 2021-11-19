import maya.cmds as cmds;
toolName = 'nurbs_curve_follow'
total_width = 225
total_height = 600

offsetScaleAttr = 'offsetScalar'
offsetStartAttr = 'offsetStart'

def nurbs_follow_UI():
    if cmds.window(toolName, exists=True):
        cmds.deleteUI(toolName)

    #create window
    window = cmds.window(toolName, title='curve follow', width=total_width, height=total_height)

    #create the main layout
    main_layout = cmds.columnLayout(width=total_width, height=total_height)
    prefix_dict = build_text_selection(window, main_layout)
    control_dict = build_control_selection(window, main_layout)
    surface_dict = build_surface_selection_frame(window, main_layout)
    math_dict = build_math_nodes_frame(window, main_layout, prefix_dict, control_dict)

    fields_dict = prefix_dict.copy()
    fields_dict.update(control_dict)
    fields_dict.update(surface_dict)
    fields_dict.update(math_dict)

    #gather all dictionaries
    build_button_grid(window, main_layout, fields_dict)

    cmds.showWindow(window)
def build_text_selection(window, main_layout):
    control_frame = cmds.frameLayout(label='Text', width=total_width, height=100,
                                     collapsable=True, parent=main_layout,
                                     collapseCommand = lambda: collapse_cmd(window, control_frame, 100),
                                     expandCommand = lambda: collapse_cmd(window, control_frame, 100, expand=True))
    rcl = Col_Layout(control_frame)

    cmds.text(label='parent identifier', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    parent_prefix_text = cmds.textField(height=20, text='parent', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)

    cmds.text(label='child identifier', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    child_prefix_text = cmds.textField(height=20, text='child', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)

    return_dict = {'prefix_parent_TF':parent_prefix_text,
                   'prefix_child_TF':child_prefix_text}
    return return_dict
def build_control_selection(window, main_layout):
    control_frame = cmds.frameLayout(label='Control Selection', width=total_width, height=175,
                                     collapsable=True, parent=main_layout,
                                     collapseCommand = lambda: collapse_cmd(window, control_frame, 175),
                                     expandCommand = lambda: collapse_cmd(window, control_frame, 175, expand=True))

    rcl = Col_Layout(control_frame)

    #parent Control
    cmds.text(label='Parent Control', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    parent_control_text = cmds.textField(height=20, parent=rcl)
    parent_load = cmds.button(label='Load', height=20, width=20,
                              command=lambda x: load_sel(parent_control_text))

    #child Control
    cmds.text(label='Child Control', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    child_control_text = cmds.textField(height=20, parent=rcl)
    child_load = cmds.button(label='Load', height=20, width=20,
                             command=lambda x: load_sel(child_control_text))

    # seperator
    cmds.separator(parent=control_frame)

    prcl = cmds.rowColumnLayout(numberOfColumns=1,
                               columnWidth=[(1, total_width)],
                               parent=control_frame)
    #connected Attribute
    cmds.text(label='Connected Axis', align='center', parent=prcl)

    #radio buttons
    check_box = cmds.checkBox(label = 'Reverse Axis', parent=prcl)
    rad_cl = cmds.rowColumnLayout(numberOfColumns=3,
                                columnWidth=[(1, total_width//3 - 10), (2, total_width//3 - 10), (3, total_width//3 - 10)],
                                columnOffset=[(1, 'both', 5), (2, 'both', 5), (3, 'both', 5)],
                                parent=prcl)
    pa_col = cmds.radioCollection(numberOfCollectionItems=3, parent=prcl)
    px = cmds.radioButton(label='X', parent=rad_cl)
    py = cmds.radioButton(label='Y', parent=rad_cl)
    pz = cmds.radioButton(label='Z', parent=rad_cl)
    #setting default value
    cmds.radioCollection(pa_col, edit=True, select=px)

    return_dict = {'parent_TF':parent_control_text,
                   'child_TF':child_control_text,
                   'axis_RC':pa_col,
                   'reverse_axis_CB':check_box}
    return return_dict
def build_surface_selection_frame(window, main_layout):
    surf_frame = cmds.frameLayout(label='Surface Selection', width=total_width, height=110,
                                  collapsable=True, parent=main_layout,
                                  collapseCommand = lambda: collapse_cmd(window, surf_frame, 110),
                                  expandCommand = lambda: collapse_cmd(window, surf_frame, 110, expand=True))

    rcl = Col_Layout(surf_frame)
    # nurbs plane
    cmds.text(label='Nurbs Plane', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    nurbs_plane = cmds.textField(height=20, parent=rcl)
    nurbs_load = cmds.button(label='Load', height=20, width=20,
                             command=lambda x:load_sel(nurbs_plane))

    #seperator
    cmds.separator(parent=surf_frame)

    prcl = cmds.rowColumnLayout(numberOfColumns=1,
                                columnWidth=[(1, total_width)],
                                parent=surf_frame)
    # connected Attribute
    cmds.text(label='Connected uv', align='center', parent=prcl)
    # radio buttons
    rad_cl = cmds.rowColumnLayout(numberOfColumns=2,
                                  columnWidth=[(1, total_width // 2 - 40), (2, total_width // 2 - 40)],
                                  columnOffset=[(1, 'both', 20), (2, 'both', 20)],
                                  parent=prcl)
    pa_col = cmds.radioCollection(numberOfCollectionItems=2, parent=prcl)
    pu = cmds.radioButton(label='U', parent=rad_cl)
    pv = cmds.radioButton(label='V', parent=rad_cl)
    # setting default value
    cmds.radioCollection(pa_col, edit=True, select=pu)

    #build dictionary
    return_dict = {'surface_TF': nurbs_plane,
                   'uv_RC': pa_col}
    return return_dict
def build_math_nodes_frame(window, main_layout, prefix_dict, control_dict):
    calc_frame = cmds.frameLayout(label='Calculation Nodes', width=total_width, height=170,
                                  collapsable=True, parent=main_layout,
                                  collapseCommand=lambda: collapse_cmd(window, calc_frame, 170),
                                  expandCommand=lambda: collapse_cmd(window, calc_frame, 170, expand=True))
    load_connections = cmds.button(label='Load Control Connections', width=total_width, height=25,
                                   parent=calc_frame)
    rcl = Col_Layout(calc_frame)

    # multiply divide parent
    cmds.text(label='parent multiply node', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    mult_parent_text = cmds.textField(height=20, editable=False, parent=rcl)
    mult_parent_load = cmds.button(label='Load', height=20, width=20,
                                   command=lambda x: load_sel(mult_parent_text))

    # multiply divide child
    cmds.text(label='child multiply node', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    mult_child_text = cmds.textField(height=20, editable=False, parent=rcl)
    mult_child_load = cmds.button(label='Load', height=20, width=20,
                                  command=lambda x: load_sel(mult_child_text))

    # plus minus
    cmds.text(label='add node', align='left', parent=rcl)
    cmds.text(label='', align='left', parent=rcl)
    add_text = cmds.textField(height=20, editable=False, parent=rcl)
    add_load = cmds.button(label='Load', height=20, width=20,
                           command=lambda x: load_sel(add_text))

    #create math_dictionary
    return_dict = {'parent_mult_TF':mult_parent_text,
                   'child_mult_TF':mult_child_text,
                   'controls_add_TF':add_text}

    #update text fields
    cmds.button(load_connections, edit=True, command=lambda x: update_math_selection(prefix_dict, control_dict, return_dict))

    return return_dict
def build_button_grid(window, main_layout, fields_dict):
    btn_col = cmds.rowColumnLayout(numberOfColumns=1, columnWidth=[(1, total_width)], parent=main_layout)
    grid_layout = cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(total_width//2, 40), parent=btn_col)
    build_btn = cmds.button(label='Build', height=40, parent=grid_layout, command = lambda x: build_network(fields_dict))
    build_btn = cmds.button(label='Close', height=40, parent=grid_layout, command = lambda x: cmds.deleteUI(toolName))

#helpers
def Col_Layout(parent):
    return cmds.rowColumnLayout(numberOfColumns=2,
                               columnWidth=[(1, 170), (2, 50)],
                               columnOffset=[(1, 'both', 5), (2, 'both', 5)],
                               parent=parent)
def load_sel(text_field):
    sel=cmds.ls(sl=True)
    if len(sel) > 0:
        cmds.textField(text_field, e=True, text=sel[0])
def update_math_selection(prefix_dict, controls_dict, math_dict):
    child_control = cmds.textField(controls_dict['child_TF'], query=True, text=True)
    parent_control = cmds.textField(controls_dict['parent_TF'], query=True, text=True)
    parent_prefix = cmds.textField(prefix_dict['prefix_parent_TF'], query=True, text=True)
    child_prefix = cmds.textField(prefix_dict['prefix_child_TF'], query=True, text=True)

    #if valid objects
    if not obj_exists(parent_control, 'parent'):
        return
    if not obj_exists(child_control, 'child'):
        return

    # checks to see connections
    parent_mult = None
    child_mult = None
    comb_add = None
    
    if attr_exists(child_control, offsetScaleAttr):
        #get both multiply divide attribute
        scalarConnList = cmds.listConnections(child_control + '.' + offsetScaleAttr, destination=True)
        if scalarConnList != None:
            for obj in scalarConnList:
                if obj.find(parent_prefix) != -1 and cmds.nodeType(obj)=='multiplyDivide':
                    parent_mult = obj
                elif obj.find(child_prefix) != -1 and cmds.nodeType(obj)=='multiplyDivide':
                    child_mult = obj
    #get rev add attribute
    if attr_exists(child_control, offsetStartAttr):
        startConnList = cmds.listConnections(child_control + '.' + offsetStartAttr, destination=True)
        if startConnList != None:
            for obj in startConnList:
                if cmds.nodeType(obj)=='plusMinusAverage':
                    comb_add = obj
            


    #set the given fields
    cmds.textField(math_dict['parent_mult_TF'], edit=True, text=parent_mult)
    cmds.textField(math_dict['child_mult_TF'], edit=True, text=child_mult)
    cmds.textField(math_dict['controls_add_TF'], edit=True, text=comb_add)
def collapse_cmd(window, frame_layout, height, expand=False):
    if not expand:
        window_height = cmds.window(window, query=True, height=True)
        frame_height=cmds.frameLayout(frame_layout, query=True, height=True)
        cmds.window(window, edit=True, height=window_height - height + 25)
        cmds.frameLayout(frame_layout, edit=True, height=25)
    else:
        window_height = cmds.window(window, query=True, height=True)
        frame_height = cmds.frameLayout(frame_layout, query=True, height=True)
        cmds.window(window, edit=True, height=window_height + height - 25)
        cmds.frameLayout(frame_layout, edit=True, height=frame_height + height - 25)
def obj_exists(object, printObject):
    if not cmds.objExists(object):
        if(object == ''):
            object = printObject
        cmds.error(object + ' does not exist')
        return False
    return True
def attr_exists(object, attribute):
    return cmds.attributeQuery(attribute, node=object, exists=True)
def add_v3_attr(object, attribute, default, minMax=None):
    current = cmds.ls(object, long=True)
    if len(current) > 1:
        cmds.error(object + 'is not a unique name')
    current = current[0]
    cmds.addAttr(current, longName=attribute, attributeType='double3')
    for axis in ['X', 'Y', 'Z']:
        if minMax != None:
            cmds.addAttr(current, longName=attribute + axis, attributeType='double', parent=attribute, min=minMax[0], max=minMax[1], defaultValue=default)
        else:
            cmds.addAttr(current, longName=attribute + axis, attributeType='double', parent=attribute, defaultValue=default)
    cmds.setAttr(current + '.' + attribute, default, default, default, type='double3')
    cmds.setAttr(current + '.' + attribute, keyable=True)
    for axis in ['X', 'Y', 'Z']:
        cmds.setAttr(current + '.' + attribute + axis, keyable=True)

def getRadioButtonText(radioCollection):
    rc = cmds.radioCollection(radioCollection, query=True, select=True)
    return cmds.radioButton(rc, query=True, label=True)

#build
def build_network(fields_dict):
    #transform nodes
    parent_control = cmds.textField(fields_dict['parent_TF'], query=True, text=True)
    child_control = cmds.textField(fields_dict['child_TF'], query=True, text=True)
    nurbs_surface = cmds.textField(fields_dict['surface_TF'], query=True, text=True)

    # if valid objects
    ident = ['parent', 'child', 'surface']
    for i, obj in enumerate([parent_control, child_control, nurbs_surface]):
        if not obj_exists(obj, ident[i]):
            return

    #detail fields
    reverse_axis = cmds.checkBox(fields_dict['reverse_axis_CB'], query=True, value=True)
    axis = getRadioButtonText(fields_dict['axis_RC']).lower()
    uv = getRadioButtonText(fields_dict['uv_RC'])

    #prefixs
    prefix_parent = cmds.textField(fields_dict['prefix_parent_TF'], query=True, text=True)
    prefix_child = cmds.textField(fields_dict['prefix_child_TF'], query=True, text=True)

    #mathNodes
    parent_mult = cmds.textField(fields_dict['parent_mult_TF'], query=True, text=True)
    if parent_mult == '':
        parent_mult = cmds.createNode('multiplyDivide',
                                      n=(child_control + '_mult').replace(prefix_child, prefix_parent))
    child_mult = cmds.textField(fields_dict['child_mult_TF'], query=True, text=True)
    if child_mult == '':
        child_mult = cmds.createNode('multiplyDivide', n=(child_control + '_mult'))
    controls_add = cmds.textField(fields_dict['controls_add_TF'], query=True, text=True)
    if controls_add == '':
        controls_add = cmds.createNode('plusMinusAverage', n=('controls_' + child_control + '_add'))

    #if attributes doesn't exist
    if not attr_exists(child_control, offsetScaleAttr):
        add_v3_attr(child_control, offsetScaleAttr, 1)
    if not attr_exists(child_control, offsetStartAttr):
        add_v3_attr(child_control, offsetStartAttr, 0.5)

    #create Follicles
    fol_shape = cmds.createNode('follicle', name=child_control.replace(prefix_child, nurbs_surface) + '_' + axis + '_follicleShape1')
    fol_transform = cmds.listRelatives(fol_shape, parent=True)[0]

    cmds.group(fol_transform, name=fol_transform + '_grp01')

    #reverse the direction
    scalar = cmds.getAttr(child_control + '.' + offsetScaleAttr + axis.upper())
    if reverse_axis:
        cmds.setAttr(child_control + '.' + offsetScaleAttr + axis.upper(), -1 * scalar)

    #connect controls to mults
    cmds.connectAttr(parent_control + '.translate', parent_mult + '.input1', f=True)
    cmds.connectAttr(child_control + '.translate', child_mult + '.input1', f=True)

    #connect child extra attr to mults
    cmds.connectAttr(child_control + '.' + offsetScaleAttr, parent_mult + '.input2', f=True)
    cmds.connectAttr(child_control + '.' + offsetScaleAttr, child_mult + '.input2', f=True)

    #connect things to adds
    cmds.connectAttr(child_control + '.' + offsetStartAttr, controls_add + '.input3D[0]', f=True)
    cmds.connectAttr(parent_mult + '.' + 'output', controls_add + '.input3D[1]', f=True)
    cmds.connectAttr(child_mult + '.' + 'output', controls_add + '.input3D[2]', f=True)

    #connect to follicle
    nurbs_surf_shape = cmds.listRelatives(nurbs_surface, shapes=True)[0]
    cmds.connectAttr(nurbs_surf_shape + '.local', fol_shape + '.inputSurface', f=True)
    cmds.connectAttr(nurbs_surf_shape + '.worldMatrix[0]', fol_shape + '.inputWorldMatrix', f=True)
    cmds.setAttr(fol_shape + '.parameterU', 0.5)
    cmds.setAttr(fol_shape + '.parameterV', 0.5)
    cmds.connectAttr(fol_shape + '.outRotate', fol_transform + '.rotate', f=True)
    cmds.connectAttr(fol_shape + '.outTranslate', fol_transform + '.translate', f=True)

    #connect from reverse multiply to the follicle
    cmds.connectAttr(controls_add + '.output3D' + axis, fol_shape + '.parameter' + uv)

    #lock transform group
    for attr in ['translate', 'rotate']:
        for axis in 'XYZ':
            cmds.setAttr(fol_transform + '.' + attr + axis, lock=True)

class CurveFollow():
    def __init__(self):
        pass
    
    def run(self):
        nurbs_follow_UI()