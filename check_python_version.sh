#!/usr/bin/env bash

dummy=$(which python)

if [ $? -ne 0 ] ; then
  echo "Couldn't find python"
  exit 1
fi

python check_python_version.py

if [ $? -ne 0 ] ; then
  exit 1
fi

# http://docs.python-guide.org/en/latest/dev/virtualenvs/
# python >= 2.7.9 has pip pre-installed; no need to install it.
pip_path=$(which pip)

if [ $? -ne 0 ] ; then
    echo "Couldn't find pip." >&2

    if [ "$OSTYPE" == "msys" ]; then
        echo "Is your python scripts directory in the path? (e.g. C:\Python27\Scripts)" >&2
    fi

    exit 1
fi

echo "Successfully checked python & pip"