#!/bin/bash
set -e

PROJECT_PATH=$(dirname $(realpath $0))

rm -rf "$PROJECT_PATH/build" "$PROJECT_PATH/dist" "$PROJECT_PATH/*.egg-info"
python3 -m pip install --editable "$PROJECT_PATH"
