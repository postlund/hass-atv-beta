#!/bin/bash

COMP_DIR=$(readlink -f `dirname "$0"`)

cmd="pytest -v --cov-report=term-missing --cov-report=html --cov homeassistant.components.apple_tv.config_flow --disable-warnings tests/components/apple_tv"
if [ "$1" = "loop" ]; then
    cmd="while true; do $cmd; echo Press enter...; read t; if [ ! "\$t" = '' ]; then break; fi; done"
elif [ $# -gt 0 ]; then
    cmd=$*
fi

docker run -it --rm \
    -v $COMP_DIR/htmlcov:/ha/htmlcov \
    -v $COMP_DIR/custom_components/apple_tv:/ha/homeassistant/components/apple_tv \
    -v $COMP_DIR/tests/apple_tv:/ha/tests/components/apple_tv \
    hadev:latest \
    bash -c "./script/gen_requirements_all.py && python3 -m script.hassfest && pip install -qqq -r requirements_test_all.txt && sed -i '/apple_tv/d' .coveragerc && $cmd"
