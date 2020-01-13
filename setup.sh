#!/bin/sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function install_failure {
   echo "INSTALL FAILED AT setup.sh:$1"   
   exit 1
}

trap 'install_failure $LINENO' ERR

./check_python_version.sh

python -m pip install --upgrade pip
pip install virtualenv

venv_name=./tmp/themes_venv
virtualenv "$venv_name" --no-download

./venv_wrapper.sh pip install --upgrade -r pip_requirements --extra-index-url https://pypi.org/simple
