import pymel.core as pm

class Overlapper:
    def __init__(self):
        pass

    def run(self):
        command = "source OverlapperRelease; OverlapperRelease;"
        print(command)
        pm.Mel.eval(command)
        return