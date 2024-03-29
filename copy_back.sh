#!/bin/bash

MANIFEST="../core/homeassistant/components/apple_tv/manifest.json"

sudo chown -R postlund:postlund ../core/tests/components/apple_tv ../core/homeassistant/components/apple_tv
sudo chmod 664 -R ../core/tests/components/apple_tv ../core/homeassistant/components/apple_tv
sudo chmod 755 ../core/tests/components/apple_tv ../core/tests/components/apple_tv/__pycache__ ../core/homeassistant/components/apple_tv ../core/homeassistant/components/apple_tv/__pycache__ ../core/homeassistant/components/apple_tv/translations


# Copy back files to core
cp -r custom_components/apple_tv/* ../core/homeassistant/components/apple_tv
cp -r custom_components/apple_tv/translations/* ../core/homeassistant/components/apple_tv/translations
cp -r tests/apple_tv/* ../core/tests/components/apple_tv

# Remove version from manifest
sed '/"version"/d' -i $MANIFEST

# Change module paths back to core
sed -i 's/custom_components.apple_tv/homeassistant.components.apple_tv/g' ../core/tests/components/apple_tv/*.py

isort ../core/homeassistant/components/apple_tv ../core/tests/components/apple_tv
black ../core/homeassistant/components/apple_tv ../core/tests/components/apple_tv
