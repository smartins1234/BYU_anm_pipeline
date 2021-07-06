import pymel.core as pm

class RemoveNamespaces:
    def __init__(self):
        pass
    def go(self):
        command = "string $pd_nsr = `promptDialog -t \"Remove Namespaces\" -message \"Namespace to Remove\" -button \"Apply!\"`;\nif ($pd_nsr == \"Apply!\") {\n\tstring $pd_nsr_text = `promptDialog -q -text $pd_nsr`;\n\tnamespace -mv $pd_nsr_text \":\" -force;\n}"
        print(command)
        pm.Mel.eval(command)
        return