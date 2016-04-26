#!/bin/bash

curl https://bootstrap.pypa.io/ez_setup.py | python
easy_install pip==1.4.1
pip install --upgrade -r pip_requirements
