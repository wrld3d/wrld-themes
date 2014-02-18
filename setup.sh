#!/bin/bash

curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python
easy_install pip==1.4.1
pip install --upgrade -r pip_requirements
