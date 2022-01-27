'''
quick utility function to check which assets have published materials
'''
import os

from pipe.pipeHandlers.project import Project
from pipe.pipeHandlers.body import Body
from pipe.pipeHandlers.body import Asset
from pipe.pipeHandlers.body import AssetType
from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

project = Project()
assets = project.list_assets()
output = "\n\n"
for name in assets:
    asset = project.get_asset(name)
    element = asset.get_element(Asset.MATERIALS)
    if element and element.get_last_version() >= 0:
        path = element.get_last_publish()[3]
        out = name + "\n"#+ " material at " + path + "\n"
        output += out

print(output)