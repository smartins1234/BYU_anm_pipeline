import os
import shutil

from pipeHandlers.body import Body, Asset, Shot, Tool, CrowdCycle, AssetType, Layout, Sequence
from pipeHandlers.element import Checkout, Element
from pipeHandlers.environment import Environment, User
from pipeHandlers import pipeline_io



class Project:
	'''
	Class describing a BYU project.
	'''

	def __init__(self):
		'''
		creates a Project instance for the currently defined project from the environment
		'''
		self._env = Environment()

	def get_name(self):
		'''
		return the name of the this project
		'''
		return self._env.get_project_name()

	def get_project_dir(self):
		'''
		return the absolute filepath to the directory of this project
		'''
		return self._env.get_project_dir()

	def get_assets_dir(self):
		'''
		return the absolute filepath to the assets directory of this project
		'''
		return self._env.get_assets_dir()

	def get_shots_dir(self):
		'''
		return the absolute filepath to the shots directory of this project
		'''
		return self._env.get_shots_dir()
	
	def get_layouts_dir(self):
		'''
		return the absolute filepath to the layouts directory of this project
		'''
		return self._env.get_layouts_dir()

	def get_sequences_dir(self):
		'''
		return the absolute filepath to the layouts directory of this project
		'''
		return self._env.get_sequences_dir()

	def get_rendered_shots_dir(self):
		rendered_shots = Environment().get_shots_dir()

		return rendered_shots

	def get_tools_dir(self):
		'''
		return the absolute filepath to the tools directory of this project
		'''
		return self._env.get_tools_dir()

		#TODO create a get tabs dir in the byuam environment module
	def get_tabs_dir(self):
		'''
		return the absolute filepath to the xml tabs directory of this project
		'''
		return os.path.join(self._env.get_project_dir(),'production/tabs')

	def get_users_dir(self):
		'''
		return the absolute filepath to the users directory of this project
		'''
		return self._env.get_users_dir()

	def get_submission_location(self):
		return pipeline_io.get_settings_info(self.get_project_dir(), "submission_location")

	def set_submission_location(self, location):
		return pipeline_io.set_settings_info(self.get_project_dir(), "submission_location", location)

	def get_user(self, username=None):
		'''
		returns a User object for the given username. If a username isn\'t given, the User object
		for the current user is returned.
		username -- (optional string) the username of the requested user
		'''
		return self._env.get_user(username)

	def get_current_username(self):
		'''
		returns the username of the current user
		'''
		return self._env.get_current_username()

	def get_asset(self, name):
		'''
		returns the asset object associated with the given name.
		name -- the name of the asset
		'''
		filepath = os.path.join(self._env.get_assets_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Asset(filepath)

	def get_shot(self, name):
		'''
		returns the shot object associated with the given name.
		name -- the name of the shot
		'''
		filepath = os.path.join(self._env.get_shots_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Shot(filepath)

	def get_tool(self, name):
		'''
		returns the tool object associated with the given name.
		name -- the name of the tool
		'''
		filepath = os.path.join(self._env.get_tools_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Tool(filepath)

	def get_sequence(self, name):
		'''
		returns the sequence object associated with the given name.
		name -- the name of the sequence
		'''
		filepath = os.path.join(self._env.get_sequences_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Sequence(filepath)
	
	def get_layout(self, name):
		'''
		returns the layout object associated with the given name.
		name -- the name of the layout
		'''
		filepath = os.path.join(self._env.get_layouts_dir(), name)
		if not os.path.exists(filepath):
			return None
		return Layout(filepath)

	def get_body(self, name):		#this needs to work. Why isn't it?
		'''
		returns the body object associated with the given name.
		name -- the name of the body
		'''
		body = self.get_asset(name)
		if body is None:
			body = self.get_tool(name)
		if body is None:
			body = self.get_shot(name)
		if body is None:
			body = self.get_layout(name)
		return body

	def create_body(self, name, bodyobj):
		'''
		If a body with that name already exists, raises EnvironmentError.
		The bodyobj is the class name for the body that will be created.
		'''
		name = pipeline_io.alphanumeric(name)
		print("name: ", name)
		filepath = os.path.join(bodyobj.get_parent_dir(), name)
		print("filepath: ", filepath)

		if name in self.list_bodies():
			print(name, " already exists, exiting...")
			return None  # body already exists

		if not pipeline_io.mkdir(filepath):
			raise OSError('couldn\'t create body directory: '+filepath)
			# some issue

		datadict = bodyobj.create_new_dict(name)
		pipeline_io.writefile(os.path.join(filepath, bodyobj.PIPELINE_FILENAME), datadict)
		new_body = bodyobj(filepath)
		for department in Asset.ALL:
			pipeline_io.mkdir(os.path.join(filepath, department))
			new_body.create_element(department, Element.DEFAULT_NAME)

		return new_body

	def create_asset(self, name, asset_type=AssetType.ASSET):
		'''
		creates a new asset with the given name, and returns the resulting asset object.
		name -- the name of the new asset to create
		'''
		asset = self.create_body(name, Asset)

		if asset is None:
			return None  # asset already exists.

		asset.update_type(asset_type)

		if asset_type == str(AssetType.SHOT):
			rendered_shots = Environment().get_shots_dir()
			dir = os.path.join(rendered_shots, name)
			pipeline_io.mkdir(dir)

		return asset

	def create_shot(self, name):
		'''
		creates a new shot with the given name, and returns the resulting shot object.
		name -- the name of the new shot to create
		'''
		shot = self.create_body(name, Shot)

		if shot is None:
			return None # shot already exists

		shot._datadict[Body.CAMERA_NUMBER] = 1
		pipeline_io.writefile(shot._pipeline_file, shot._datadict)

		return shot

	def create_layout(self, name):
		layout = self.create_body(name, Layout)

		if layout is None:
			return None # set already exists

		return layout

	def create_sequence(self, name):
		sequence = self.create_body(name, Sequence)

		if sequence is None:
			return None # set already exists

		return sequence

	def create_tool(self, name):
		'''
		creates a new tool with the given name, and returns the resulting tool object.
		name -- the name of the new tool to create
		'''
		return self.create_body(name, Tool)

	def _list_bodies_in_dir(self, filepath, filter=None):
		dirlist = os.listdir(filepath)

		bodylist = []
		for bodydir in dirlist:
			abspath = os.path.join(filepath, bodydir)
			if os.path.exists(os.path.join(abspath, Body.PIPELINE_FILENAME)):
				bodylist.append(bodydir)
			else:
				print("path doesn't exist for ", bodydir)
		bodylist.sort()

		if filter is not None and len(filter)==3:
			filtered_bodylist = []
			for body in bodylist:
				bodyobj = self.get_body(body)
				if bodyobj.has_relation(filter[0], filter[1], filter[2]):
					filtered_bodylist.append(body)
			bodylist = filtered_bodylist

		return bodylist

	def list_assets(self):
		path = self._env.get_assets_dir() + ".asset_list.txt"
		assets = []
		f = open(path, "r")
		for aName in f:
			if aName[-1] == "\n":  # remove newline character
				aName = aName[:-1]
			assets.append(aName)

		assets.sort(key=str.lower)
		return assets

	def list_existing_assets(self):
		list = self._list_bodies_in_dir(self._env.get_assets_dir())
		assets = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.ASSET:
				assets.append(str(item))
		assets.sort(key=str.lower)
		return assets

	def list_assets_short(self):
		path = self._env.get_assets_dir() + ".short_asset_list"
		assets = []
		f = open(path, "r")
		for aName in f:
			if aName[-1] == "\n":
				aName = aName[:-1]
			assets.append(aName)

		assets.sort(key=str.lower)
		return assets

	def list_shots(self):
		path = self._env.get_shots_dir() + ".shot_list"
		shots = []
		f = open(path, "r")
		for shot in f:
			if shot[-1] == "\n": #remove newline character
				shot = shot[:-1]
			shots.append(shot)

		shots.sort(key=str.lower)
		return shots

	'''def list_existing_shots(self):
		list = self._list_bodies_in_dir(self._env.get_shots_dir())
		shots = []

		for item in list:
			shot = self.get_shot(item)
			if asset.get_type() == AssetType.ASSET:
				assets.append(str(item))
		assets.sort(key=str.lower)
		return assets'''

	def list_layouts(self):
		path = self._env.get_layouts_dir() + ".layout_list"
		layouts = []
		f = open(path, "r")
		for layout in f:
			if layout[-1] == "\n": #remove newline character
				layout = layout[:-1]
			layouts.append(layout)

		layouts.sort(key=str.lower)
		return layouts

	def list_sequences(self):
		path = self._env.get_sequences_dir() + ".sequence_list"
		sequences = []
		f = open(path, "r")
		for sequence in f:
			if sequence[-1] == "\n":
				sequence = sequence[:-1]
			sequences.append(sequence)

		sequences.sort(key=str.lower)
		return sequences

	def list_existing_shots(self, filter=None):
		'''
		returns a list of strings containing the names of all shots in this project
		filter -- a tuple containing an attribute (string) relation (operator) and value
				e.g. (Shot.FRAME_RANGE, operator.gt, 100). Only returns shots whose
				given attribute has the relation to the given desired value. Defaults to None.
		'''
		list = self._list_bodies_in_dir(self._env.get_shots_dir())

		shot_list = []

		for item in list:
			shot = self.get_shot(item)
			if shot.get_type() == AssetType.SHOT:
				shot_list.append(str(item))

		shot_list.sort(key=str.lower)

		return shot_list

	def list_existing_layouts(self):
		layouts = self._list_bodies_in_dir(self._env.get_layouts_dir())

		layouts_list = []

		for item in layouts:
			layouts_list.append(str(item))

		layouts_list.sort(key=str.lower)
		return layouts_list

	def list_tools(self):
		'''
		returns a list of strings containing the names of all tools in this project
		'''
		list = self._list_bodies_in_dir(self._env.get_tools_dir())
		tool_list = []

		for item in list:
			tool = self.get_tool(item)
			if tool.is_tool():
				tool_list.append(str(item))

		tool_list.sort(key=str.lower)

		return tool_list

	def list_hdas(self):
		'''
		returns a list of strings containing the names of all tools in this project
		'''
		hdas = os.listdir(self._env.get_hda_dir())
		names = []
		for hda in hdas:
			name, ext = os.path.splitext(hda)

			if not ext:
				continue

			if str(ext) == ".hda":
				names.append(name)

		return names

	def list_sets(self):
		'''
		returns a list of strings containing the names of all sets in this project
		'''
		list = self._list_bodies_in_dir(self._env.get_assets_dir())
		set_list = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.SET:
				set_list.append(str(item))

		set_list.sort(key=str.lower)

		return set_list

	def list_actors(self):
		list = self._list_bodies_in_dir(self._env.get_assets_dir())
		actors = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.ACTOR:
				actors.append(str(item))

		actors.sort(key=str.lower)

		return actors

	def list_props(self):
		list = self._list_bodies_in_dir(self._env.get_assets_dir())
		props = []

		for item in list:
			asset = self.get_asset(item)
			if asset.get_type() == AssetType.PROP:
				props.append(str(item))

		props.sort(key=str.lower)

		return props

	def list_bodies(self):
		'''
		returns a list of strings containing the names of all bodies (assets and shots)
		'''
		return self.list_existing_assets() + self.list_existing_shots() + self.list_tools() + self.list_existing_layouts()

	def list_users(self):
		'''
		returns a list of strings containing the usernames of all users working on the project
		'''
		users_dir = self._env.get_users_dir()
		dirlist = os.listdir(users_dir)
		userlist = []
		for username in dirlist:
			userfile = os.path.join(users_dir, username, User.PIPELINE_FILENAME)
			if os.path.exists(userfile):
				userlist.append(username)
		userlist.sort()
		return userlist

	def is_checkout_dir(self, path):
		'''
		returns True if the given path is a valid checkout directory
		returns False otherwise
		'''
		return os.path.exists(os.path.join(path, Checkout.PIPELINE_FILENAME))

	def get_checkout(self, path):
		'''
		returns the Checkout object describing the checkout operation at the given directory
		If the path is not a valid checkout directory, returns None
		'''
		if not self.is_checkout_dir(path):
			return None
		return Checkout(path)

	def get_checkout_element(self, path):
		'''
		returns the checked out element from the checkout operation at the given directory
		If the path is not a valid checkout directory, returns None
		'''
		checkout = self.get_checkout(path)
		if checkout is None:
			return checkout
		body = self.get_body(checkout.get_body_name())
		element = body.get_element(checkout.get_department_name(), checkout.get_element_name())
		return element

	def delete_shot(self, shot):
		'''
		delete the given shot
		'''
		if shot in self.list_shots():
			shutil.rmtree(os.path.join(self.get_shots_dir(), shot))

	def delete_asset(self, asset):
		'''
		delete the given asset
		'''
		if asset in self._list_bodies_in_dir(self._env.get_assets_dir()):
			shutil.rmtree(os.path.join(self.get_assets_dir(), asset))

	def delete_tool(self, tool):
		'''
		delete the given tool
		'''
		if tool in self.list_tools():
			shutil.rmtree(os.path.join(self.get_tools_dir(), tool))

	def delete_crowd_cycle(self, crowd_cycle):
		'''
		delete the given crowd cycle
		'''
		if crowd_cycle in self.list_crowd_cycles():
			shutil.rmtree(os.path.join(self.get_crowds_dir(), crowd_cycle))

	def delete_ribs_for_bodies(self, bodies):
		for body in bodies:
			body = self.get_body(body)
			element = body.get_element(Department.RIB_ARCHIVE)

			rib_cache_dir = element.get_cache_dir()
			try:
				# delete the rib cache dir
				shutil.rmtree(rib_cache_dir)

			except:
				# create a new cache dir
				pipeline_io.mkdir(rib_cache_dir)


		print("deleted ribs for " + str(bodies))
