#!/bin/bash

DIRS="custom_components/apple_tv/ tests/apple_tv"

for d in $DIRS
do
    pushd $d
    echo "* Formatting in $d"
    black *.py
    isort *.py
    flake8 --max-line-length=88 --ignore=E501,W503,E203,D202,W504 *.py
    popd
done
