#!/bin/bash

function install_failure {
   echo "INSTALL FAILED AT setup.sh:$1"
   popd
   exit 1
}

trap 'install_failure $LINENO' ERR

python -m pip install --upgrade pip
pip install --upgrade -r pip_requirements
