'''ref = hou.node("/stage").createNode("reference")
ref.parm("filepath1").set("/users/animation/secybyu/cube.usd")

rop = hou.node("/stage").createNode("usd_rop")
rop.setInput(0, ref)
rop.parm("enableoutputprocessor_simplerelativepaths").set(0)
rop.parm("lopoutput").set("/users/animation/secybyu/bash_test.usda")

rop.parm("execute").pressButton()'''

import subprocess
output = subprocess.run(["hython", "/groups/cenote/BYU_anm_pipeline/pipe/tools/mayaTools/exporters/houdini_usd2.py"])

print(output.returncode)