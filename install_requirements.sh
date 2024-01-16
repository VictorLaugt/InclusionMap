#!/bin/bash
rm -f inclusion_map/requirements.txt
pipreqs inclusion_map
pip install -r inclusion_map/requirements.txt
