import pymel.core as pm

'''
runs a mel script to remove all unknown nodes
'''
class rmNodes:
    def __init__(self):
        pass

    def go(self):
        command = "{\nstring $unknownNodes[] = `lsType unknown`;\nfor($node in $unknownNodes){\nif($node==\"<done>\")\nbreak;\nif(`objExists $node`)\n{\nint $lockState[] = `lockNode -q -l $node`;\nif($lockState[0]==1)\nlockNode -l off $node;\ndelete $node;\n}\n}\n}"
        pm.Mel.eval(command)
        return