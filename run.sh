#!/bin/bash

COMP_DIR=$(readlink -f `dirname "$0"`)
TO_INSERT="async def async_setup_entry(hass, entry):\n    \"\"\"To comment.\"\"\"\n    return await hass.data\[DOMAIN\].async_setup_entry\(entry\)\n\n\nasync def async_unload_entry(hass, entry):\n    \"\"\"To comment.\"\"\"\n    return await hass.data\[DOMAIN\].async_unload_entry\(entry\)"

if grep docker /proc/1/cgroup -qa; then
    cmd="pytest -v --cov-report=term-missing --cov-report=html --cov homeassistant.components.apple_tv.config_flow --disable-warnings tests/components/apple_tv"
    if [ "$1" = "loop" ]; then
        cmd="while true; do $cmd; echo Press enter...; read t; if [ ! "\$t" = '' ]; then break; fi; done"
    elif [ $# -gt 0 ]; then
        cmd=$*
    fi

    sed -i 's%class RemoteDevice(ToggleEntity):%'"$TO_INSERT"'\n\n\nclass RemoteDevice(ToggleEntity):%' homeassistant/components/remote/__init__.py

    ./script/gen_requirements_all.py
    python3 -m script.hassfest
    pip install -qqq -r requirements_test_all.txt
    sed -i '/apple_tv/d' .coveragerc
    $cmd

else
    docker run -it --rm \
        -v $COMP_DIR/htmlcov:/ha/htmlcov \
	-v $COMP_DIR/run.sh:/ha/run.sh \
        -v $COMP_DIR/custom_components/apple_tv:/ha/homeassistant/components/apple_tv \
        -v $COMP_DIR/tests/apple_tv:/ha/tests/components/apple_tv \
        hadev:latest \
	bash -c "$0 $*"
fi

