from pipe.tools.houdiniTools import *
from pipe.tools.houdiniTools.creator import creator as hou_creator
from pipe.tools.houdiniTools.assembler import assembler as hou_assembler
from pipe.tools.houdiniTools.cloner import cloner as hou_cloner
from pipe.tools.houdiniTools.cloner import anim_cloner# as hou_cloner
from pipe.tools.houdiniTools.publisher import mat_publisher as hou_publisher
from pipe.tools.houdiniTools.publisher import shot_publisher
from pipe.tools.houdiniTools.cloner import unpacker as hou_unpacker
from pipe.tools.houdiniTools.updater import update_assets as hou_updater
from pipe.tools.houdiniTools.updater import update_shots
#from pipe.tools.houdiniTools.cloner import parser as hou_parser
import pipe.pipeHandlers.quick_dialogs as qd


class ReloadScripts:

    def run(self):
        reload(utils.reload_scripts)
        reload(hou_assembler)
        reload(hou_creator)
        reload(hou_cloner)
        reload(hou_publisher)
        reload(hou_unpacker)
        reload(hou_updater)
        reload(anim_cloner)
        reload(update_shots)
        #reload(hou_parser)
        reload(qd)
