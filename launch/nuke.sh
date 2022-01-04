#!/bin/sh
SOURCEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "$SOURCEDIR"
source $SOURCEDIR/env.sh
export CURRENT_PROGRAM='nuke'

export NUKE_PATH=${MEDIA_PROJECT_DIR}/pipe/tools/nukeTools:${MEDIA_PROJECT_DIR}/pipe/tools/nukeTools/NukeSurvivalToolkit

/opt/Nuke13.0v3/Nuke13.0