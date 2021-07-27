import hou
from functools import partial
from distutils.version import StrictVersion
import pipe.pipeHandlers.quick_dialogs as qd

import pipe.pipeHandlers.select_from_list as sfl

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

import os
import inspect

# TODO: make versioning automatic
# allow input of a note to explain what's changed? Could possibly do this in help per version, but looking it up might not be terribly helpful
# do we need to be able to load new versions of assets? It would be nice. I don't know if we need notes. Possibly open up a file showing the changes for each version?
# idea: load and display (in a houdini window) a text file displaying information about each version.


class Publisher:
    def __init__(self):
        print("starting publisher")
        self.body = None
        self.fileName = None
        self.element = None

    def export_usd_files():
        # TODO: export usd from the whole asset node tree to the asset folder (same as .body)
        pass

    # command necessary for publish_asset dialog box to load correctly
    def set_new_version_button_command(self, node, version_window):
        """
        :param node: hou.Node
        :param version_window: VersionWindow
        :return: None
        """
        library_filepath = node.type().definition().libraryFilePath()
        name_base = '::'.join(node.type().name().split('::')[:-1])
        new_version = '{major}.{minor}.{revision}'.format(major=version_window.major_version.value(),
                                                          minor=version_window.minor_version.value(),
                                                          revision=version_window.revision_version.textFromValue(
            version_window.revision_version.value()))
        new_name = '{name_base}::{new_version}'.format(
            name_base=name_base, new_version=new_version)
        # Here we can compare the current version to new version and detect if the new version is lower or equal
        if not StrictVersion(new_version) > StrictVersion(node.type().nameComponents()[-1]):
            hou.ui.displayMessage(
                'The version number is the same as the current version - please increase number')
            return
        # Create a pop up to give the user a chance to confirm or cancel
        answer = hou.ui.displayMessage('Creating a new version for {node_name}\nNew Version - {new_version}'.format(node_name=node.type().name(), new_version=new_version),
                                       title='Setting New Version',
                                       buttons=['OK', 'Cancel'])

        # If answer 'OK', create new version and set to latest version
        if answer == 0:
            node.type().definition().copyToHDAFile(library_filepath, new_name)
            all_definitions = hou.hda.definitionsInFile(library_filepath)
            node.changeNodeType(all_definitions[-1].nodeTypeName())
            # Close version window

    def publish_asset(self):
        '''
        this is what's called when the button is pushed.
        '''
        # copied from cloner
        project = Project()

        asset_list = project.list_assets()
        self.item_gui = sfl.SelectFromList(
            l=asset_list, parent=hou.ui.mainQtWindow(), title="Select an asset to publish")
        # call asset results function here to be used once selected
        self.item_gui.submitted.connect(self.asset_results)
        # end copy

    def asset_results(self, value):
        self.fileName = value[0]
        selection = hou.selectedNodes()
        # If it is more than one or none, abort
        if len(selection) != 1:
            qd.error(
                'Please select a single Houdini Digital Asset node to save and update version on.')
            return
        # If it is not a Houdini Digital Asset, abort
        if not selection[0].type().definition():
            qd.error(
                'Please select a single Houdini Digital Asset node to save and update version on.')
            return

        hda_node = selection[0]
        definition = hda_node.type().definition()
        libraryFilePath = definition.libraryFilePath()
        self.filepath = libraryFilePath
        '''current_full_name = hda_node.type().name()

        # last index is current version
        current_version_string = hda_node.type().nameComponents()[-1]
        #current_major = current_version_string.split('.')[0]
        #print('major version is ' + current_major)
        #current_minor = current_version_string.split('.')[1]
        # Set the 3 digit revision number to 0 if the HDA is only using the single float versioning (1.0 and not 1.0.005)
        current_revision = 0 if len(current_version_string.split(
            '.')) < 3 else current_version_string.split('.')[2]
        all_definitions = hou.hda.definitionsInFile(libraryFilePath)
        # This sets the node to the latest version of those stored
        hda_node.changeNodeType(all_definitions[-1].nodeTypeName())'''
        definition.updateFromNode(hda_node)

        self.body = Project().create_asset(self.fileName)
        if self.body is None:
            self.body = Project().get_asset(self.fileName)
        if self.body is None:
            print("Stephanie did an oopsie whoopsie :'(")
            return

        self.input = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment ")
        self.input.submitted.connect(self.comment_results)

    def comment_results(self, value):
        comment = str(value)
        path = os.path.join(self.body.get_filepath(), Asset.HDA)
        self.element = Element(path)
        
        username = Environment().get_user().get_username()

        name = self.fileName
        self.element.update_app_ext(".hda")
        self.element.publish(username, self.filepath, comment, name)
        # this bit will display the version info. Probably unneeded, as we'll be using element stuff instead.
        #f = open('/users/animation/martinje/Desktop/info.txt', 'r')
        #file_contents = f.read()
        # print(file_contents)
        # f.close()

        # qd.info(file_contents)

        # Instantiate the VersionWindow class - at this point, I would jump over to that code - keep in mind, we will
        # return a window object and afterwards we will set its initial state, using everything we just learned about
        # this HDA.

        #version_window = qd.VersionWindow(hou.qt.mainWindow())
        #version_window.setWindowTitle('Versioning for: {hda_name}'.format(hda_name=current_full_name))
        # version_window.current_version_label.setText(current_version_string)
        # version_window.current_path_label.setText(libraryFilePath)
        # Set value of the integer editor and set the editor to not go down from there
        # version_window.major_version.setValue(int(current_major))
        # version_window.major_version.setMinimum(int(current_major))
        # Set value of the integer editor and set the editor to not go down from there
        # version_window.minor_version.setValue(int(current_minor))
        # version_window.minor_version.setMinimum(int(current_minor))
        # Set value of the integer editor and set the editor to not go down from there
        # version_window.revision_version.setValue(int(current_revision))
        # version_window.revision_version.setMinimum(int(current_revision))
        # Connect the button signal to the set new version command and pass the hda node and the version window as arguments
        #version_window.set_version.clicked.connect(partial(self.set_new_version_button_command, hda_node, version_window))
        # Show the window
        # version_window.show()

    def publish_tool(self):
        pass

    def publish_shot(self):
        '''
        publishes shot (entire .hip file). Nothing needs to be selected for this to work.
        '''
        scene = hou.hipFile.name()
        print('file name is ' + scene)

        project = Project()     # get project and its shots
        asset_list = project.list_shots()

        self.item_gui = sfl.SelectFromList(l=asset_list, parent=hou.qt.mainWindow(
        ), title="Select a shot to publish to, my friend.")
        self.item_gui.submitted.connect(self.shot_results)

    def shot_results(self, value):
        # chosen shot is the only asset in the list
        self.chosen_shot = value[0]

        self.comment = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comments?")
        self.comment.submitted.connect(self.shot_comment)

    def shot_comment(self, value):
        # hou.hipFile.setName('newName_v01')  #this will change the name of the file: can be versioned. So that's nice.
        comment = value
        if comment is None:
            comment = "Publish by " + \
                str(user.get_username()) + \
                '. Ask them to leave a comment next time lol'
        # FIXME: make variable more specific to shot?
        chosen_shot = self.chosen_shot
        project = Project()

        print('Selected shot name: ' + chosen_shot)
        # print(project.get_body(chosen_shot))
        shot_body = project.create_shot(chosen_shot)
        if shot_body is None:
            shot_body = project.get_shot(chosen_shot)
        if shot_body is None:
            print("Something is horribly wrong. Talk to Stephanie")
            return
        filepath = shot_body.get_filepath()
        shot_element = shot_body.get_element("hip")
        shot_element.update_app_ext(".hip")
        prev_vers = shot_element.get_last_version()
        # path = os.path.abspath(inspect.getfile(project.get_body(chosen_shot)))      #trying to get path here.
        filepath = os.path.join(shot_element._filepath, chosen_shot + ".hip")
        #
        print('file path is ', filepath)
        hou.hipFile.setName(filepath)
        src = hou.hipFile.save()
        # # hou.hipFile.saveAndIncrementFileName()      #this actually works! Dunno if I want to use it though.
        #
        # #Publish
        user = Environment().get_user().get_username()
        pipeline_io.set_permissions(src)
        # try that asset name is body name.
        dst = self.publish_element(shot_element, user, filepath, comment)
        #pipeline_io.set_permissions(dst)
        #
        # message = "Successfully published " + str(self.body.get_name()) + "!"
        # self.print_success_message(message)

    def publish_element(self, element, user, src, comment="None"):
        print('username is', user.get_username())
        dst = element.publish(user.get_username(), src,
                              comment, self.chosen_shot)

        # Ensure file has correct permissions
        # Permissions are actually taken care of as part of the element.publish() function, so this isn't necessary
        '''try:
            os.chmod(dst, 0660)
        except Exception as e:
            print("Error setting file permissions: " + str(e))'''

        return dst

    def publish_layout(self):
        if len(hou.selectedNodes()) != 1:
            qd.error("Select only the last node in the network")
            return

        layout_list = Project().list_layouts()

        self.item_gui = sfl.SelectFromList(l=layout_list, parent=hou.qt.mainWindow(), title="Which layout are you publishing?")
        self.item_gui.submitted.connect(self.layout_results)

    def layout_results(self, value):
        self.layout_name = value[0]
        self.layout = Project().get_layout(self.layout_name)
        if self.layout is None:
            self.layout = Project().create_layout(self.layout_name)
        if self.layout is None:
            qd.error("Stephanie done messed up")
            return
        self.element = self.layout.get_element(Asset.LAYOUT)

        # make a USD ROP node
        rop = hou.node("/stage").createNode("usd_rop")
        # connect the selected node to the ROP
        out = hou.selectedNodes()[0]
        rop.setInput(0, out)
        # set the necessary values in the ROP
        self.savePath = os.path.join(self.element._filepath, self.layout_name + ".usda")
        rop.parm("lopoutput").set(self.savePath)
        rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
        # save to disk
        rop.parm("execute").pressButton()

        # publish :)
        self.comment = qd.HoudiniInput(
            parent=hou.qt.mainWindow(), title="Comment for publish?")
        self.comment.submitted.connect(self.layout_comment)

    def layout_comment(self, value):
        comment = value[0]
        username = Environment().get_user().get_username()
        self.element.update_app_ext(".usda")
        self.element.publish(username, self.savePath, comment, self.layout_name)

        if self.element.get_last_version() == 0:
            # if it is the first publish, we have to make the referencing file as well
            # create a reference node
            ref = hou.node("/stage").createNode("reference")
            # set the values to reference the main publish file, etc.
            ref.parm("primpath").set("/layout")
            ref.parm("filepath1").set(self.element.get_last_publish()[3])          
            # create a USD ROP node and connect it to the ref node
            refrop = hou.node("/stage").createNode("usd_rop")
            refrop.setInput(0, ref)
            # set the values in the ROP and save to disk alongside the main publish
            refrop.parm("lopoutput").set(os.path.join(self.element._filepath, self.layout_name + "_ref.usda"))
            refrop.parm("enableoutputprocessor_simplerelativepaths").set(0)
            refrop.parm("execute").pressButton()
            #   this only needs to be done once since with every new publish, the file being referenced gets updated
            ref.destroy()
            refrop.destroy()



