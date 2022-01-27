import pymel.core as pm

'''
runs a mel script for the Rigging team
'''
class createControl:
    def __init__(self):
        pass

    def run(self):
        command = "source macConCreate; macConCreate;"
        print(command)
        pm.Mel.eval(command)
        return