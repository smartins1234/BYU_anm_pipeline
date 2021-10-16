#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "$SOURCEDIR"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='houdini'

# Will find the installation of Houdini on the PATH if $HFS is not set
if [ ! $HFS ]
then
  hfs_location=("`which houdini`")
  echo "$hfs_location"
  if [ -z $hfs_location ]
  then
    echo "No houdini command found on the PATH."
    return -1
  fi
  hou_binary=$(realpath $hfs_location)
  #use this if you want to use a specific version of houdini
  #hou_binary="/opt/hfs18.5.351/bin/houdini"
  echo "$hou_binary"
  export HFS="$(cd "$( dirname "${hou_binary}" )" && cd ../ && pwd )"
  echo "$HFS"
fi

# source current houdini setup
cd ${HFS}
source ./houdini_setup
cd -

# We need this line in order for gridmarkets to work.
#export HOUDINI_USE_HFS_PYTHON=1
export JOB=${MEDIA_PROJECT_DIR}
HOUDINI_TOOLS=${MEDIA_PROJECT_DIR}/pipe/tools/houdiniTools
export PYTHONPATH=${PYTHONPATH}:${HOUDINI_TOOLS}
export HOUDINI_PATH=${HOUDINI_PATH}:${HOUDINI_TOOLS}"/custom;&":${HOUDINI_TOOLS}:${MEDIA_PROJECT_DIR}"/production;&":${MEDIA_PROJECT_DIR}"/production/tools;&"
export HOUDINI_DSO_PATH=${HOUDINI_DSO_PATH}:${MEDIA_PROJECT_DIR}"/production/dso;&"

export HOUDINI_MENU_PATH=${HOUDINI_TOOLS}"/custom/menu;&"
export HOUDINI_TOOLBAR_PATH=${MEDIA_PROJECT_DIR}"/production/tabs;&"
export HOUDINI_UI_ICON_PATH=${MEDIA_PROJECT_DIR}"icons/tool-icons;&"

export HSITE = ${HOUDINI_TOOLS}"/custom;&"
#export HOUDINI_USER_PREF_DIR=${MEDIA_PROJECT_DIR}"/production/users/"${USER}";&"
export HOUDINI_DESK_PATH=${HOUDINI_DESK_PATH}:${HOUDINI_TOOLS}"/custom/menu;&"

#set the colorspace by default
export OCIO="/opt/hfs18.5.596/houdini/ocio/config.ocio"
export OCIO_ACTIVE_DISPLAYS="rec709"
export OCIO_ACTIVE_VIEWS="rec709"

export RMANTREE="/opt/pixar/RenderManProServer-24.1"
export RFHTREE="/opt/pixar/RenderManForHoudini-24.1"
export RMAN_PROCEDURALPATH=$RFHTREE/18.5.596/openvdb:&
export HOUDINI_PATH=${HOUDINI_PATH}:$RFHTREE"/18.5.596:&"

echo "Starting Houdini..."
cd ~/
gnome-terminal -e "houdinifx -foreground $@"
cd -
$SHELL
