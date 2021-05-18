import importlib as il
from pipe.tools.mayaTools import *
from pipe.tools.mayaTools.cloners import cloner as maya_cloner
#from pipe.tools.mayaTools.creators import creator as maya_creator
#from pipe.tools.mayaTools.publishers import publisher as maya_publisher
from pipe.tools.mayaTools.utilities import utils as maya_utils
from pipe.tools.mayaTools.utilities import reload_scripts
#from pipe.tools.mayaTools.utils import education as edu
#from pipe.tools.mayaTools.exporters import alembic_exporter as alembic_exporter
#from pipe.tools.mayaTools.exporters import fbx_exporter as fbx_exporter
#from pipe.tools.mayaTools.exporters import exporter as exporter
#from pipe.tools.mayaTools.exporters import json_exporter as json_exporter
#from pipe.tools.mayaTools.importers import referencer as maya_referencer
#from pipe.tools.mayaTools.importers import reference_importer as reference_importer
#from pipe.tools.mayaTools.exporters import tagger as maya_tagger
#from pipe.tools.mayaTools.submitters import playblaster as maya_playblaster

from pipe.pipeHandlers import select_from_list as sfl


class ReloadScripts:

    def go(self):
        il.reload(reload_scripts)
        #reload(maya_creator)
        il.reload(maya_cloner)
        #reload(maya_publisher)
        il.reload(maya_utils)
        #reload(edu)
        #reload(alembic_exporter)
        #reload(fbx_exporter)
        #reload(exporter)
        #reload(json_exporter)
        #reload(maya_referencer)
        #reload(reference_importer)
        #reload(maya_tagger)
        #reload(maya_playblaster)
        il.reload(sfl)