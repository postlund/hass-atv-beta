#!/bin/bash

COMP_DIR=$(readlink -f `dirname "$0"`)

if grep docker /proc/1/cgroup -qa; then
    if [ ! -x "/ha/venv" ]; then
        python -m venv venv
    fi
    source venv/bin/activate
    python setup.py develop

    cmd="pytest -vv --cov-report=term-missing --cov-report=html --cov homeassistant.components.apple_tv.config_flow --disable-warnings tests/components/apple_tv"
    if [ "$1" = "loop" ]; then
        cmd="while true; do $cmd; echo Press enter...; read t; if [ ! "\$t" = '' ]; then break; fi; done"
    elif [ $# -gt 0 ]; then
        cmd=$*
    fi

    ./script/gen_requirements_all.py
    python3 -m script.hassfest
    pip install tox
    pip install -qqq -r requirements_test_all.txt
    pip uninstall -y asyncio typing
    sed -i '/apple_tv/d' .coveragerc
    $cmd

else
    docker run -it --rm --net=host \
        -v $COMP_DIR/../home-assistant:/ha  \
        -v $COMP_DIR/../conf:/ha/conf  \
        -v $COMP_DIR/htmlcov:/ha/htmlcov \
        -v $COMP_DIR/custom_components/apple_tv:/ha/homeassistant/components/apple_tv \
        -v $COMP_DIR/tests/apple_tv:/ha/tests/components/apple_tv \
        -v $COMP_DIR/run.sh:/ha/run.sh \
        hadev:latest \
	bash -c "$0 $*"
fi
