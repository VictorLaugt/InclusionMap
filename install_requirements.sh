#!/bin/bash
set -e

PROJECT_PATH=$(dirname $(realpath $0))

rm -f "$PROJECT_PATH/inclusion_map/requirements.txt"
pipreqs "$PROJECT_PATH/inclusion_map"

cd "$PROJECT_PATH"
pip install -r "inclusion_map/requirements.txt"
