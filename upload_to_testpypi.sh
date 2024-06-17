#!/bin/bash
set -e

PROJECT_PATH=$(dirname $(realpath $0))

rm -rf "$PROJECT_PATH/build" "$PROJECT_PATH/dist" "$PROJECT_PATH/*.egg-info"
python3 "$PROJECT_PATH/setup.py" sdist bdist_wheel
twine upload -r testpypi "$PROJECT_PATH/dist/*"
