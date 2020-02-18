#!/bin/bash

set -e

DIRS="custom_components/apple_tv/ tests/apple_tv"

for d in $DIRS
do
    black $d/*.py
    isort $d/*.py
done
