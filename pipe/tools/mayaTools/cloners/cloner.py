import pipe.pipeHandlers.select_from_list as sfl
import pipe.pipeHandlers.quick_dialogs as qd
from pipe.tools.mayaTools.utilities.utils import *
from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.element import Element

from PySide2 import QtWidgets
import maya.cmds as mc
import pymel.core as pm
import maya.OpenMayaUI as omu
import os


class Cloner:
	def __init__(self):
		pass

	def rollback(self):
		#this was obviously never implemented
		print("Rollin' Rollin' Rollin' (Back)")

	def quick_clone(self):
		'''
		Clone the most recent version by default
		'''
		self.quick = True
		self.go()

	def clone(self, quick=True):
		self.quick = quick
		self.project = Project()

		type_list = ["Model", "Rig", "Animation", "Camera"]
		self.item_gui = sfl.SelectFromList(
		    l=type_list, parent=maya_main_window(), title="Select a type of asset to clone")
		self.item_gui.submitted.connect(self.type_results)


	def type_results(self, value):
		self.type = value[0]
		print(self.type)

		if self.type == "Model":
			self.clone_geo()
		elif self.type == "Rig":
			self.clone_rig()
		elif self.type == "Animation":
			self.clone_anim()
		elif self.type == "Camera":
			self.clone_camera()
		else:
			qd.error("Stephanie did something wrong, go complain to her :)")
			return

	def non_gui_open(self, filePath=None, assetName='Temp'):
		if filePath == None:
			print('no file')
			return
		if os.path.exists(filePath):
			mc.file(filePath, open=True, force=True, ignoreVersion=True)
			print("open file " + assetName)
		else:
			print('File does not exist: '+assetName)

	def clone_geo(self):
		self.type = Asset.GEO

		asset_list = self.project.list_existing_assets()
		self.item_gui = sfl.SelectFromList(
		    l=asset_list, parent=maya_main_window(), title="Select a model to clone")
		self.item_gui.submitted.connect(self.results)

	def clone_rig(self):

		self.type = Asset.RIG

		asset_list = self.project.list_existing_assets()
		self.item_gui = sfl.SelectFromList(
		    l=asset_list, parent=maya_main_window(), title="Select a rig to clone")
		self.item_gui.submitted.connect(self.results)

	def clone_anim(self):
		pm.loadPlugin("AbcImport")
		self.type = Asset.ANIMATION

		shot_list = self.project.list_existing_shots()
		self.item_gui = sfl.SelectFromList(
		    l=shot_list, parent=maya_main_window(), title="Select a shot to clone")
		self.item_gui.submitted.connect(self.shot_results)

	def clone_camera(self):
		pm.loadPlugin("AbcImport")
		self.type = Asset.CAMERA

		shot_list = self.project.list_existing_shots()
		self.item_gui = sfl.SelectFromList(
		    l=shot_list, parent=maya_main_window(), title="Select a shot to clone")
		self.item_gui.submitted.connect(self.shot_results)

	def shot_results(self, value):
		shot_name = value[0]
		print(shot_name)
		self.shot = self.project.get_body(shot_name)

		if self.type == Asset.CAMERA:
			self.element = self.shot.get_element(Asset.CAMERA)
			cam_list = next(os.walk(self.element._filepath))[1]
			for name in cam_list:
				if not name.startswith(Asset.CAMERA):
					cam_list.remove(name)

			cam_list.sort(key=str.lower)
			print(cam_list)
			self.item_gui = sfl.SelectFromList(
			    l=cam_list, parent=maya_main_window(), title="Select a camera to clone")
			self.item_gui.submitted.connect(self.results)

		elif self.type == Asset.ANIMATION:
			self.element = self.shot.get_element(Asset.ANIMATION)
			asset_list = next(os.walk(self.element._filepath))[1]
			for name in asset_list:
				if name == "cache":
					asset_list.remove(name)

			asset_list.sort(key=str.lower)
			print(asset_list)
			self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to clone")
			self.item_gui.submitted.connect(self.results)

	def asset_results(self, value):
		asset_name = value[0]
		print(asset_name)

		self.type = os.path.join(self.type, asset_name)

	def get_asset(self, value):
		asset_name = value[0]
		print(asset_name)
		self.type = os.path.join(self.type, asset_name)

		shot_list = self.project.list_existing_shots()
		self.item_gui = sfl.SelectFromList(
		    l=shot_list, parent=maya_main_window(), title="Select the shot to clone")
		self.item_gui.submitted.connect(self.results)

	def go(self):
		project = Project()
		asset_list = project.list_assets()
		self.item_gui = sfl.SelectFromList(
		    l=asset_list, parent=maya_main_window(), title="Select an asset to clone")
		self.item_gui.submitted.connect(self.results)

	def results(self, value):
		print("Final value: ", value[0])
		filename = value[0]
		self.namespace = filename

		if self.type == Asset.GEO or self.type == Asset.RIG:
			body = self.project.get_body(filename)
			self.body = body
			element = self.body.get_element(self.type)
		else:
			self.body = self.shot
			element = self.body.get_element(os.path.join(self.type, filename))

		if element is None:
			qd.warning("Nothing was cloned.")
			return

		self.element = element

		if self.quick:
			latest = element.get_last_publish()
			if not latest:
				qd.error("There have been no publishes in this department.")
				return
			else:
				selected_scene_file=latest[3]

				#if we're cloning a model, lets make sure we're getting the obj instead of the usda
				if self.type == Asset.GEO:
					path = selected_scene_file.split(".")
					selected_scene_file = path[0] + ".obj"

				self.open_scene_file(selected_scene_file)
				return

		self.publishes = element.list_publishes()
		print("publishes: ", self.publishes)

		if not self.publishes:
			qd.error("There have been no publishes in this department.")
			return

		# make the list a list of strings, not tuples
		self.sanitized_publish_list=[]
		for publish in self.publishes:
			label=publish[0] + " " + publish[1] + " " + publish[2]
			self.sanitized_publish_list.append(label)

		self.item_gui = sfl.SelectFromList(
		    l=self.sanitized_publish_list, parent=maya_main_window(), title="Select publish to clone")
		self.item_gui.submitted.connect(self.publish_selection_results)

	def publish_selection_results(self, value):

		selected_publish=None
		for item in self.sanitized_publish_list:
			if value[0] == item:
				selected_publish=item

		selected_scene_file=None
		position = 0
		for publish in self.publishes:
			label=publish[0] + " " + publish[1] + " " + publish[2]
			if label == selected_publish:
				version_path = self.element.get_version_dir(position)
				version_path = os.path.join(version_path, self.name + self.element.get_app_ext())
				selected_scene_file = version_path
				break
			position += 1

		# selected_scene_file is the one that contains the scene file for the selected commit
		self.open_scene_file(selected_scene_file)

	def open_scene_file(self, selected_scene_file):
		if selected_scene_file is not None:

			if not os.path.exists(selected_scene_file):
				qd.error("That publish is missing. It may have been deleted to clear up space.")
				return False

			else:
				if self.type == Asset.RIG or self.type == Asset.ANIMATION or self.type == Asset.CAMERA:
					# reference in the file
					mc.file(selected_scene_file, r=True, ignoreVersion=True, mnc=False, gl=True, ns=":")
					print("File referenced: " + selected_scene_file)
				elif self.type == Asset.GEO:
					# check for import vs reference
					im = qd.binary_option("Do you want to import or reference this asset?", "Import", "Reference")
					if im:
						# import the geometry
						mc.file(selected_scene_file, i=True, ignoreVersion=True, mnc=False, gl=True, ns=":")
						print("File imported: " + selected_scene_file)
					else:
						# reference the geometry
						mc.file(selected_scene_file, r=True, ignoreVersion=True, mnc=False, gl=True, ns=":")
						print("File referenced: " + selected_scene_file)
				else:
					# reference the file
					mc.file(selected_scene_file, r=True, ignoreVersion=True, mnc=False, gl=True, ns=":")
					print("File referenced: " + selected_scene_file)

			return True
		else:
			return False
