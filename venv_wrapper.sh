#!/bin/sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function trap_failure {
   echo "FAILED AT venv_wrapper.sh:$1"   
   exit 1
}

trap 'trap_failure $LINENO' ERR
venv_name=./tmp/themes_venv

# the wonderful world of cross-platform venv support ...  
if [ "$OSTYPE" == "msys" ]; then
    source "$venv_name"/Scripts/activate
else
    source "$venv_name"/bin/activate
fi

echo "Running command with python virtual env: $VIRTUAL_ENV"

"$@"