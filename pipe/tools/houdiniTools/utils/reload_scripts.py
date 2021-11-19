from pipe.tools.houdiniTools import *
from pipe.tools.houdiniTools.creator import creator as hou_creator
from pipe.tools.houdiniTools.assembler import assembler as hou_assembler
from pipe.tools.houdiniTools.cloner import cloner as hou_cloner
from pipe.tools.houdiniTools.cloner import anim_cloner# as hou_cloner
from pipe.tools.houdiniTools.cloner import tool_cloner
from pipe.tools.houdiniTools.cloner import camera_cloner
from pipe.tools.houdiniTools.cloner import mat_cloner
from pipe.tools.houdiniTools.cloner import light_cloner
from pipe.tools.houdiniTools.publisher import mat_publisher as hou_publisher
from pipe.tools.houdiniTools.publisher import shot_publisher
from pipe.tools.houdiniTools.publisher import light_publisher_2
from pipe.tools.houdiniTools.publisher import tool_publisher
from pipe.tools.houdiniTools.publisher import obj_publisher
from pipe.tools.houdiniTools.publisher import seq_fx_publisher
from pipe.tools.houdiniTools.cloner import unpacker as hou_unpacker
from pipe.tools.houdiniTools.updater import update_assets as hou_updater
from pipe.tools.houdiniTools.updater import update_shots
from pipe.tools.houdiniTools.cloner import layout_unpacker
from pipe.tools.houdiniTools.cloner import parser
#from pipe.tools.houdiniTools.cloner import parser as hou_parser
import pipe.pipeHandlers.quick_dialogs as qd


class ReloadScripts:

    def run(self):
        reload(utils.reload_scripts)
        reload(hou_assembler)
        reload(hou_creator)
        reload(hou_cloner)
        reload(tool_cloner)
        reload(camera_cloner)
        reload(mat_cloner)
        reload(light_cloner)
        reload(hou_publisher)
        reload(shot_publisher)
        reload(light_publisher_2)
        reload(tool_publisher)
        reload(obj_publisher)
        reload(seq_fx_publisher)
        reload(hou_unpacker)
        reload(hou_updater)
        reload(anim_cloner)
        reload(update_shots)
        reload(layout_unpacker)
        reload(parser)
        
        #reload(hou_parser)
        reload(qd)
