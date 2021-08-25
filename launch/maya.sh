#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='maya'

export MAYA_SHELF_DIR=${MEDIA_PROJECT_DIR}'/pipe/tools/mayaTools/custom/'
export MAYA_ICONS_DIR=${MEDIA_PROJECT_DIR}'/icons/'
export PYTHONPATH=${PYTHONPATH}:${MEDIA_PROJECT_DIR}'/production/tools'
export MAYAUSD_EXPORT_MAP1_AS_PRIMARY_UV_SET=1
export MAYAUSD_IMPORT_PRIMARY_UV_SET_AS_MAP1=1

# env vars for USD
# USD_INSTALL_ROOT='/usr/local/USD/build/USD'
# export MAYA_PLUG_IN_PATH=${MAYA_PLUG_IN_PATH}:$USD_INSTALL_ROOT'/third_party/maya/plugin/'
# export MAYA_SCRIPT_PATH=${MAYA_SCRIPT_PATH}:$USD_INSTALL_ROOT'/third_party/maya/lib/usd/usdMaya/resources/':$USD_INSTALL_ROOT'/third_party/maya/plugin/pxrUsdPreviewSurface/resources/'
# export PYTHONPATH=${PYTHONPATH}:'/usr/local/USD/lib/python'
# export XBMLANGPATH=${XBMLANGPATH}:$USD_INSTALL_ROOT'/third_party/maya/lib/usd/usdMaya/resources/'

echo "Starting Maya..."
maya -script ${MEDIA_PROJECT_DIR}/pipe/tools/mayaTools/custom/shelf.mel &
