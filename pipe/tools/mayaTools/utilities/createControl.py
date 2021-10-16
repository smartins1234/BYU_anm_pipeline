import pymel.core as pm

class createControl:
    def __init__(self):
        pass

    def run(self):
        command = "source macConCreate; macConCreate;"
        print(command)
        pm.Mel.eval(command)
        return