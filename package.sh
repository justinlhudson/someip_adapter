#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

rm -rf $SCRIPT_DIR/build/*
rm -rf $SCRIPT_DIR/*.egg-info
rm -rf $SCRIPT_DIR/dist/*

#read -p "Press enter to continue"

python setup.py build
python setup.py install
python setup.py bdist_wheel
#wheel convert $SCRIPT_DIR/dist/*
find $SCRIPT_DIR/ -type f -name "*.whl" | xargs wheel tags --remove --python-tag=py3 --abi-tag=none
pip install --force-reinstall .